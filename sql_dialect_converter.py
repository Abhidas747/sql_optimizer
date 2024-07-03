import csv
from langchain_community.llms import Ollama

# Initialize the Ollama model
llm = Ollama(model="codegemma")

# List of known SQL dialects
KNOWN_DIALECTS = [
    "ANSI SQL", "MySQL", "PostgreSQL", "SQLite", "Microsoft SQL Server (T-SQL)",
    "Oracle Database (PL/SQL)", "IBM Db2", "Sybase", "Teradata", "Amazon Redshift",
    "Snowflake", "MariaDB", "SAP HANA", "Cassandra (CQL)", "Google BigQuery",
    "Amazon Aurora", "Greenplum", "Netezza (IBM PureData)", "Informix", "Firebird",
    "Apache Derby", "H2", "HSQLDB (HyperSQL)", "VoltDB", "MemSQL (SingleStore)",
    "TimescaleDB", "CockroachDB", "CrateDB", "Actian Matrix", "MonetDB",
    "Azure SQL Database", "Vertica", "YugabyteDB (YCQL)", "Presto (Trino)",
    "Druid SQL", "Trafodion", "Altibase", "InterBase", "QuasarDB",
    "Faircom c-treeACE", "Aster Data", "FoxPro (Visual FoxPro)", "Paradox",
    "Empress"
]


def identify_sql_dialect(query):
    prompt = f"Identify the SQL dialect (PL/SQL, Snowflake, MySQL, PostgreSQL, SQL Server, etc.) of the following query:\n\n{query}\n\nDialect:"
    response = llm.invoke(prompt)

    # Handle cases where response is not structured as expected
    if isinstance(response, str):
        first_line = response.split('\n')[0].strip()  # Get the first line and strip any leading/trailing whitespace
    else:
        # Handle cases where response is structured
        if 'output' in response and response['output']:
            first_line = response['output'][0].get('text', 'No response found').split('\n')[0].strip()
        else:
            first_line = 'No response found'

    # Filter response to match known dialects
    for dialect in KNOWN_DIALECTS:
        if dialect.lower() in first_line.lower():
            return dialect

    return 'Unknown'


def convert_sql_to_dialect(query, target_dialect):
    prompt = f"Convert the following SQL query to {target_dialect} dialect and return only the SQL query, not itsexplanation:\n\nOriginalQuery:\n\n{query}\n\nConverted Query in {target_dialect} Dialect:"

    response = llm.invoke(prompt)

    # Handle cases where response is not structured as expected
    if isinstance(response, str):
        return response.strip()  # Return the string response directly, stripped of leading/trailing whitespace

    # Handle cases where response is structured
    if 'output' in response and response['output']:
        return response['output'][0].get('text', 'No response found').strip()
    else:
        return 'No response found'


def process_sql_queries(input_file, output_file, target_dialect):
    with open(input_file, mode='r', newline='', encoding='utf-8') as csv_input, \
            open(output_file, mode='w', newline='', encoding='utf-8') as csv_output:
        reader = csv.reader(csv_input)
        writer = csv.writer(csv_output)

        # Write header for the output CSV
        writer.writerow(['Original SQL Query', 'Original Dialect', 'Converted SQL Query'])

        for line in reader:
            query = line[0]  # Assuming SQL query is in the first column

            # Identify SQL dialect
            original_dialect = identify_sql_dialect(query)

            # Convert SQL query to target dialect
            converted_query = convert_sql_to_dialect(query, target_dialect)

            # Write to output CSV
            writer.writerow([query, original_dialect, converted_query])

    print(f"Processed {input_file} and saved results to {output_file}")


# Example usage
input_file = 'non_optimized_sql_queries.csv'
output_file = 'output_sql_converter.csv'
target_dialect = 'Snowflake'  # Specify the target dialect

process_sql_queries(input_file, output_file, target_dialect)