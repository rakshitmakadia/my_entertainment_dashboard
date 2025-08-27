import os
from google.oauth2.service_account import Credentials
from google.auth import default
from googleapiclient.discovery import build
import constants


SERVICE_ACCOUNT_FILE = 'myentertainmentproject.json'
SCOPES = constants.SCOPES
SPREADSHEET_ID = constants.SPREADSHEET_ID
SHEET_NAME = constants.SHEET_NAME

def write_df_to_google_sheet(df):
    """
    Writes a pandas DataFrame to a specified Google Sheet using the Sheets API.
    The function authenticates using either a service account file or Application Default Credentials (ADC) via Workload Identity Federation.
    It converts the DataFrame to string values, writes the column headers and data to the specified sheet and range, and returns a status message
    with details about the update.
    Args:
        df (pandas.DataFrame): The DataFrame to write to the Google Sheet.
    Returns:
        str: A status message indicating the updated range, number of rows (including headers), and total cells updated.
    Raises:
        googleapiclient.errors.HttpError: If the Sheets API request fails.
        FileNotFoundError: If the service account file is specified but not found.
        Exception: For other authentication or API errors.
    Note:
        Requires the following global variables to be defined:
            - SERVICE_ACCOUNT_FILE: Path to the service account credentials JSON file.
            - SCOPES: List of OAuth scopes required for the Sheets API.
            - SPREADSHEET_ID: The ID of the target Google Spreadsheet.
            - SHEET_NAME: The name of the target sheet within the spreadsheet.
    """
    
    if os.path.exists(SERVICE_ACCOUNT_FILE):
        print("Using service account credentials...")
        creds = Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE, scopes=SCOPES)
    else:
        print("Using Workload Identity Federation (ADC)...")
        creds, _ = default(scopes=SCOPES)

    google_sheet_service = build('sheets', 'v4', credentials=creds)

    df = df.astype(str)
    values = [df.columns.tolist()] + df.values.tolist()
    update_body = {
        'values': values
    }

    result = google_sheet_service.spreadsheets().values().update(
            spreadsheetId=SPREADSHEET_ID,
            range=f"{SHEET_NAME}!A1",
            valueInputOption='RAW',
            body=update_body
    ).execute()

    status = f"Updated range {result.get('updatedRange')} with {result.get('updatedRows')} rows including headers and total {result.get('updatedCells')} cells updated."

    return status
