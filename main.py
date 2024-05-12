import subprocess
import pandas as pd

# Run kathmandupost.py
subprocess.run(['python', 'kathmandupost.py'])

# Run setopati.py
subprocess.run(['python', 'setopati.py'])

# Wait for the scripts to finish and check for successful execution
kathmandupost_process = subprocess.run(['python', 'kathmandupost.py'])
setopati_process = subprocess.run(['python', 'setopati.py'])

if kathmandupost_process.returncode == 0 and setopati_process.returncode == 0:
    # Read the CSV files
    df_1 = pd.read_csv('kathmandupost.csv')
    df_2 = pd.read_csv('setopati.csv')

    # Concatenate the dataframes
    concatenated_df = pd.concat([df_1, df_2])

    # Drop duplicates based on all columns
    df_no_duplicates = concatenated_df.drop_duplicates()

    # Save the DataFrame without duplicates back to a CSV file
    df_no_duplicates.to_csv('all_csv_no_duplicates.csv', index=False)

    # Read the filtered CSV file into a DataFrame
    df_filtered = pd.read_csv('all_csv_no_duplicates.csv')

    # Remove rows where "Heading" or "Content" contains "Heading not found" or "Content not found"
    df_filtered = df_filtered[~df_filtered['Heading'].str.contains('Heading not found') & ~df_filtered['Content'].str.contains('Content not found')]

    # Save the filtered DataFrame to a new CSV file
    df_filtered.to_csv('Filtered_data.csv', index=False, sep=';')

    # Display the resulting DataFrame
    print(df_filtered)
    print("Data processing completed.")
else:
    print("Error: One or more scripts failed to execute.")
