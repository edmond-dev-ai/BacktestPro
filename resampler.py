# resampler.py - A Python script for time-series data resampling.

import sys
import pandas as pd
import io
import json

def resample_data(csv_data_string, rule):
    """
    Uses the pandas library to resample daily OHLCV data to a new timeframe.
    - csv_data_string: A string containing the daily data in CSV format.
    - rule: The pandas resampling rule (e.g., '1H' for 1 hour, '4H' for 4 hours).
    """
    # Read the CSV data from the string passed by Node.js into a pandas DataFrame.
    # 'index_col=0' sets the first column (the date) as the DataFrame's index.
    # 'parse_dates=True' tells pandas to interpret the index column as datetime objects.
    try:
        df = pd.read_csv(io.StringIO(csv_data_string), index_col=0, parse_dates=True)
    except Exception as e:
        # If there's an error reading the data, print it to stderr and exit.
        print(f"Error reading CSV data in Python: {e}", file=sys.stderr)
        sys.exit(1)

    # Define the aggregation logic for creating the new, lower-timeframe bars.
    ohlc_rules = {
        'open': 'first',  # The open of the new bar is the first price in the period.
        'high': 'max',    # The high is the maximum price in the period.
        'low': 'min',     # The low is the minimum price in the period.
        'close': 'last',  # The close is the last price in the period.
        'volume': 'sum'   # The volume is the sum of all volume in the period.
    }

    # Apply the resampling rule. This groups the data by the specified time rule.
    # .dropna() removes any periods that don't contain any data (e.g., weekends for hourly data).
    resampled_df = df.resample(rule).apply(ohlc_rules).dropna()
    
    # Convert the datetime index back to a string in ISO 8601 format.
    # This is a standard format that JavaScript can easily parse.
    resampled_df.index = resampled_df.index.strftime('%Y-%m-%dT%H:%M:%S')

    # Return the resulting DataFrame as a JSON string.
    # 'orient="table"' creates a structured JSON that is easy to parse in JavaScript.
    return resampled_df.to_json(orient='table', index=True)

if __name__ == "__main__":
    # The first command-line argument passed from Node.js is the resampling rule (e.g., '1H').
    target_rule = sys.argv[1]
    
    # Read all data piped from the Node.js process's standard input.
    input_data = sys.stdin.read()

    # Run the main resampling function.
    result_json = resample_data(input_data, target_rule)
    
    # Print the final JSON string to standard output, so the Node.js process can capture it.
    print(result_json)
