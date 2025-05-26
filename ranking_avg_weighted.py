import pandas as pd
import glob
import os
import re

# Define year weights for 2018 to 2024
year_weights = {
    '2018': 1,
    '2019': 2,
    '2020': 3,
    '2021': 4,
    '2022': 5,
    '2023': 6,
    '2024': 7
}

# Path to CSVs
data_dir = 'data'  # Change if needed

# Compute weighted average for rank metrics
def weighted_avg(group):
    total_weight = group['Weight'].sum()
    return pd.Series({
        'Avg Preference Rank': round((group['Preference_Rank'] * group['Weight']).sum() / total_weight, 2),
        'Avg Opening Rank': round((group['Opening_Rank'] * group['Weight']).sum() / total_weight),
        'Avg Closing Rank': round((group['Closing_Rank'] * group['Weight']).sum() / total_weight)
    })

def calculate_averages(filter):

    pattern = os.path.join(data_dir, f"*_{filter}_program_ranks.csv")
    files = sorted(glob.glob(pattern))


    print("📂 Found files:", len(files))

    all_dfs = []

    # Filter only files from 2018 onwards
    for f in files:
        match = re.search(r'(\d{4})', os.path.basename(f))
        if not match:
            continue
        year = match.group(1)
        if year not in year_weights:
            continue
        df = pd.read_csv(f)
        df['Year'] = int(year)
        df['Weight'] = year_weights[year]
        all_dfs.append(df)

    if not all_dfs:
        raise ValueError("❌ No valid data found from 2018 onwards.")

    combined_df = pd.concat(all_dfs, ignore_index=True)

    # Group by unique program
    summary = (
        combined_df
            .groupby(['Institute', 'Academic Program Name', 'Quota'])
            .apply(weighted_avg, include_groups=False)
            .reset_index()
    )

    # Sort based on avg preference rank
    summary = summary.sort_values(by='Avg Preference Rank').reset_index(drop=True)

    # Save to CSV
    output_file = f"{data_dir}/{filter}_program_weighted_average_rankings.csv"
    summary.to_csv(output_file, index=False)

    print(f"✅ Weighted average summary saved to: {output_file}")


calculate_averages("noniit")
calculate_averages("iit")

