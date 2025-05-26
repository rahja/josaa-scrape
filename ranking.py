#!/usr/bin/env python
# coding: utf-8

# In[15]:


import pandas as pd
import glob
import os


# Directory where CSV files are stored

# In[16]:


data_dir = 'data'  # You can change this if your CSVs are in a different folder


# Define the range of years to process

# In[17]:


years = list(range(2018, 2025))


# In[25]:


def process_data(all_data, filter):

    if filter == "noniit":
        # Apply Non-IIT filters and use .copy() to avoid SettingWithCopyWarning
        filtered = all_data[
            ~all_data['Institute'].str.contains("Indian Institute of Technology", case=False, na=False) &
            ~all_data['Academic Program Name'].str.lower().str.contains("bachelor of architecture|bachelor of planning", na=False) &
            all_data['Quota'].isin(['AI', 'OS']) &
            all_data['Seat Type'].isin(['OPEN']) &
            (all_data['Gender'] == 'Gender-Neutral')
        ].copy()
    elif filter == "iit":
        # Apply IIT+Arch filters and use .copy() to avoid SettingWithCopyWarning
        filtered = all_data[
            all_data['Institute'].str.contains("Indian Institute of Technology", case=False, na=False) &
            all_data['Quota'].isin(['AI', 'OS']) &
            all_data['Seat Type'].isin(['OPEN']) &
            (all_data['Gender'] == 'Gender-Neutral')
        ].copy()
    else:
        print("Unknown filter, exiting.")
        sys.exit()

    # Drop rows with invalid (NaN) ranks
    filtered = filtered.dropna(subset=['Opening Rank', 'Closing Rank'])
    # Convert 'col1' to integer type
    filtered['Opening Rank'] = filtered['Opening Rank'].astype(int)
    filtered['Closing Rank'] = filtered['Closing Rank'].astype(int)
    
    # Group by program and find min Opening Rank and max Closing Rank across rounds
    grouped = (
        filtered
        .groupby(['Institute', 'Academic Program Name', 'Quota'])
        .agg(
            Opening_Rank=('Opening Rank', 'min'),
            Closing_Rank=('Closing Rank', 'max')
        )
        .reset_index()
    )

    # Sort by Closing Rank and assign preference rank
    grouped = grouped.sort_values(by='Closing_Rank').reset_index(drop=True)
    grouped['Preference_Rank'] = grouped.index + 1

    # Save the output for this year
    output_file = f"{data_dir}/{year}_{filter}_program_ranks.csv"
    grouped.to_csv(output_file, index=False)
    print(f"✅ Saved: {output_file}")


# In[ ]:


for year in years:
    # Get all files for the given year (e.g., 2020-1.csv, 2020-2.csv)
    round_files = sorted(glob.glob(os.path.join(data_dir, f"{year}-*.csv")))
    if not round_files:
        print(f"⚠️  No files found for {year}. Skipping.")
        continue
    print(f"📥 Processing year {year} with {len(round_files)} rounds...")

    # Concatenate all rounds for the year
    all_data = pd.concat([pd.read_csv(f) for f in round_files], ignore_index=True)
    process_data(all_data, "noniit")
    process_data(all_data, "iit")
    
print("\n🏁 All years processed successfully!")

