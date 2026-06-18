## sources/user-network-fs/gcsfuse/perfmetrics/scripts/gsheet/gsheet_test.py

Purpose: Unit tests for the Google Sheets helper.

APIs and control flow: Tests `_get_sheets_service_client` by replacing credential loading and asserting a discovery `Resource`, tests `write_to_google_sheet` by mocking chained Sheets API calls and expected get/clear/update arguments, and tests permission failure by injecting an `HttpError`.

State and persistence: No real Sheets access because service calls are mocked. The credential test still builds a discovery resource.

Dependencies and risks: Monkeypatches `service_account.Credentials.from_service_account_file` directly rather than using a context manager. The mocked fluent API uses broad `MagicMock`, so it checks call shape but not actual API request validity.

Test signals: Verifies write path call sequence and error propagation.
