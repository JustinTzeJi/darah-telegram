import os
import pandas as pd
import pandas_gbq

os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "/app/.cred/creds.json"

granular = "https://storage.data.gov.my/healthcare/blood_donation_retention_2024.parquet"
donations_state = "https://raw.githubusercontent.com/MoH-Malaysia/data-darah-public/main/donations_state.csv"

if __name__ == "__main__":
    print(os.listdir("/app/.cred/"))
    granular_df = pd.read_parquet(granular)

    granular_df.to_gbq(destination_table="data_darah.blood-donation-retention", project_id="articulate-case-410317", if_exists = "replace")

    donations_state_df = pd.read_csv(donations_state)

    donations_state_df.to_gbq(destination_table="data_darah.donations_state", project_id="articulate-case-410317", if_exists = "replace")

