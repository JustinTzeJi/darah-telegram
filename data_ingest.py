import os
import pandas as pd
import pandas_gbq

os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "/app/.cred/creds.json"

granular = "https://storage.data.gov.my/healthcare/blood_donation_retention_2024.parquet"
donations_state = "https://raw.githubusercontent.com/MoH-Malaysia/data-darah-public/main/donations_state.csv"

if __name__ == "__main__":
    granular_df = pd.read_parquet(granular)

    pandas_gbq.to_gbq(granular_df, "data_darah.blood-donation-retention", project_id="articulate-case-410317", if_exists = "replace")

    donations_state_df = pd.read_csv(donations_state)

    pandas_gbq.to_gbq(donations_state_df, "data_darah.donations_state", project_id="articulate-case-410317", if_exists = "replace")

