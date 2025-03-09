import os
import logging
from pyspark.sql import SparkSession
from pyspark.sql.functions import col, to_timestamp, regexp_extract, DataFrame

# Create logs directory if not exists
LOG_DIR = "/Users/E-commerce Sales Data 2024/E-commerce_venv/logs/"
if not os.path.exists(LOG_DIR):
    os.makedirs(LOG_DIR)

# Configure Logging
LOG_FILE_PATH = os.path.join(LOG_DIR, "ecommerce_etl.log")
logging.basicConfig(
    filename=LOG_FILE_PATH,
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

class EcommerceETL:
    def __init__(self, database_url, database_properties, jar_path):
        self.database_url = database_url
        self.database_properties = database_properties
        self.spark = self.init_spark(jar_path)
    
    def init_spark(self, jar_path):
        """Initialize Spark session."""
        try:
            spark = SparkSession.builder \
                .appName("E-commerce ETL") \
                .config("spark.jars", jar_path) \
                .getOrCreate()
            logger.info("Spark Session initialized successfully")
            return spark
        except Exception as e:
            logger.error(f"Error initializing Spark: {e}")
            raise

    def load_csv(self, file_path):
        """Loads CSV file into a DataFrame."""
        try:
            df = self.spark.read.csv(file_path, header=True, inferSchema=True)
            logger.info(f"Loaded CSV: {file_path}")
            return df
        except Exception as e:
            logger.error(f"Error loading CSV {file_path}: {e}")
            raise

    def write_to_postgres(self, df, table_name, mode="append"):
        """Writes a DataFrame to PostgreSQL."""
        try:
            df.write.jdbc(self.database_url, table_name, mode=mode, properties=self.database_properties)
            logger.info(f"Successfully written to PostgreSQL: {table_name}")
        except Exception as e:
            logger.error(f"Error writing to PostgreSQL {table_name}: {e}")

    def read_from_postgres(self,table_name):
        """Read data from a PostgreSQL table and return a Spark DataFrame."""
        try:
            df = self.spark.read.jdbc(self.database_url, table_name, properties=self.database_properties)
            logger.info(f"Successfully read from PostgreSQL: {table_name}")
            return df  # Return DataFrame
        except Exception as e:
            logger.error(f"Error reading from PostgreSQL {table_name}: {e}")
            return None  # Return None if reading fails
        
    def transform_customers(self, df):
    #Transforms the Customers DataFrame while keeping all original columns."""
        """Transforms the Customers DataFrame."""
        return df.select(
            col("Customer ID").alias("customer_id").cast("int"),
            col("Age").alias("age").cast("int"),
            col("Gender").alias("gender"),
            col("Location").alias("location"),
            col("Review Rating").alias("review_rating").cast("float"),
            col("Subscription Status").alias("subscription_status"),
            col("Frequency of Purchases").alias("frequency_of_purchases")
        )

    def transform_products(self, df):
        """Transforms the Products DataFrame."""
        return df.select(
            col("Uniqe Id").alias("product_id").cast("string"),
            col("Product Name").alias("product_name"),
            col("Brand Name").alias("brand_name"),
            col("Category").alias("category"),
            col("Model Number").alias("model_number"),
            col("Size Quantity Variant").alias("size"),
            col("Color").alias("color"),
            col("Dimensions").alias("dimensions"),
            col("Shipping Weight").alias("shipping_weight").cast("decimal(10,2)"),
            regexp_extract(col("Selling Price"), r"\$([\d,]+\.?\d*)", 1).alias("selling_price").cast("decimal(10,2)"),
            col("Stock").alias("stock").cast("int"),
            col("Quantity").alias("quantity").cast("int"),
            col("Product URL").alias("product_url"),
            col("Product Description").alias("product_description")
        )
    
    def transform_transactions(self, transactions_df, customers_df):
        """Transforms transactions and customers, then joins them into a final DataFrame."""

        return transactions_df.withColumn("purchase_date", to_timestamp(col("Time stamp"), "dd/MM/yyyy H:mm")) \
            .select(
                col("user id").alias("customer_id").cast("int"),
                col("product id").alias("product_id").cast("string"),
                col("purchase_date")
            ).dropna(subset=["purchase_date"]) \
            .join(
                customers_df.select(
                    col("Customer ID").alias("customer_id").cast("int"),
                    col("Purchase Amount (USD)").alias("purchase_amount_usd").cast("decimal(10,2)"),
                    col("Shipping Type").alias("shipping_type"),
                    col("Discount Applied").alias("discount_applied").cast("decimal(5,2)"),
                    col("Promo Code Used").alias("promo_code_used"),
                    col("Payment Method").alias("payment_method")
                ),
                on="customer_id",
                how="left"
            )

    def transform_interactions(self, transactions_df):
        """Creates Interactions Table."""
        return transactions_df.select(
            col("customer_id").alias("user_id"),
            col("product_id").cast("string"),
            col("purchase_date").alias("timestamp"),
            col("payment_method").alias("interaction_type")  
        )
    
    def transform_discounts(self, transactions_df: DataFrame) -> DataFrame:
        """Transforms the transactions DataFrame to extract discount-related data."""
        if transactions_df is None:
            raise ValueError("transactions_df is None. Check if the table was read correctly.")

        return transactions_df.select(
            col("transaction_id"),
            col("promo_code_used"),
            col("discount_applied").cast("decimal(5,2)"),
            col("customer_id").cast("int"),
            col("product_id").cast("string"),
            col("purchase_date").cast("timestamp")
        ).where(col("promo_code_used").isNotNull())

    def transform_product_categories(self, products_df):
        """Creates Product Categories Table."""
        return products_df.select(
            col("product_id").alias("category_id").cast('string'),
            col("category").alias("category_name")
        ).distinct()
    
    def transform_product_variants(self, products_df):
        """Creates Product Variants Table with cleaned data."""

        product_variants_df = products_df.select(
            col("product_id").cast("string"),
            col("size"),
            col("color"),
            col("quantity").alias("stock_quantity").cast("int")
        )

        # Fill NULL values with defaults
        product_variants_df = product_variants_df.fillna({
            "size": "Unknown", 
            "color": "Unknown", 
            "stock_quantity": 0
        })

        # Remove duplicates
        product_variants_df = product_variants_df.distinct()

        # Print summary for debugging
        product_variants_df.select(["size", "color", "stock_quantity"]).summary("count", "min", "max").show()

        return product_variants_df


    def run_etl(self, customer_path, product_path, transaction_path):
        """Executes the full ETL pipeline."""
        try:
            logger.info("Starting ETL Process...")

            # Load Data
            customers_df = self.load_csv(customer_path)
            products_df = self.load_csv(product_path)
            transactions_df = self.load_csv(transaction_path)

            # Transform Data
            customers_transform_df = self.transform_customers(customers_df)
            products_transform_df = self.transform_products(products_df)
            transactions_transform_df = self.transform_transactions(transactions_df, customers_df)
            
            customers_transform_df.show(5)
            products_transform_df.show(5)
            transactions_transform_df.show(5)

            interactions_df = self.transform_interactions(transactions_transform_df)
            read_from_transactions_df = self.read_from_postgres("transactions")
            discounts_df = self.transform_discounts(read_from_transactions_df)
            product_categories_df = self.transform_product_categories(products_transform_df)
            product_variants_df = self.transform_product_variants(products_transform_df)

            # Write to PostgreSQL
            self.write_to_postgres(customers_transform_df, "customers")
            self.write_to_postgres(products_transform_df, "products")
            self.write_to_postgres(transactions_transform_df, "transactions")
            self.write_to_postgres(interactions_df, "interactions")
            self.write_to_postgres(discounts_df, "discounts")
            self.write_to_postgres(product_categories_df, "product_categories")
            self.write_to_postgres(product_variants_df, "product_variants")
            
            logger.info("ETL Process Completed Successfully")

        except Exception as e:
            logger.error(f"ETL Process Failed: {e}")
        finally:
            self.spark.stop()
            logger.info("Spark Session Stopped")


# Database Configuration
DATABASE_URL = "jdbc:postgresql://localhost:5432/ecommerce_db"
DATABASE_PROPERTIES = {
    "user": "postgres",
    "password": "postgres",
    "driver": "org.postgresql.Driver",
    "stringtype": "unspecified"
}
JAR_PATH = "/Users/E-commerce Sales Data 2024/E-commerce_venv/postgresql-42.5.1.jar"

# File Paths
CUSTOMER_PATH = "/Users/E-commerce Sales Data 2024/E-commerce_venv/Data/customer_details.csv"
PRODUCT_PATH = "/Users/E-commerce Sales Data 2024/E-commerce_venv/Data/product_details.csv"
TRANSACTION_PATH = "/Users/E-commerce Sales Data 2024/E-commerce_venv/Data/E-commerece_sales_data_2023.csv"

# Run ETL
if __name__ == "__main__":
    etl = EcommerceETL(DATABASE_URL, DATABASE_PROPERTIES, JAR_PATH)
    etl.run_etl(CUSTOMER_PATH, PRODUCT_PATH, TRANSACTION_PATH)
