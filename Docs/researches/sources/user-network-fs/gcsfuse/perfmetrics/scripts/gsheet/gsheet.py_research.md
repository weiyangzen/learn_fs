## sources/user-network-fs/gcsfuse/perfmetrics/scripts/gsheet/gsheet.py

Purpose: Minimal Google Sheets writer for perf metrics.

APIs and control flow: `_get_sheets_service_client` loads service-account credentials from `./gsheet/creds.json` with spreadsheets scope and builds a Sheets v4 client. `write_to_google_sheet(worksheet, data, spreadsheet_id)` reads column A to determine occupied rows, clears `A2:<last>`, and writes provided rows starting at `A2` with `USER_ENTERED` input.

State and persistence: Mutates the target spreadsheet by clearing old rows and replacing data. Reads local credentials.

Dependencies and risks: Assumes the worksheet exists and the get response contains `values`; empty sheets without `values` can raise `KeyError`. Clearing range format uses `A2:<row>` without a column on the end, which relies on API interpretation.

Test signals: `gsheet_test` mocks service calls and verifies get/clear/update plus HttpError propagation.
