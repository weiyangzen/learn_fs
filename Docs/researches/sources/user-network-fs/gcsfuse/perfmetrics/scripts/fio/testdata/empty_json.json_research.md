## sources/user-network-fs/gcsfuse/perfmetrics/scripts/fio/testdata/empty_json.json

Purpose: Negative parser fixture for syntactically valid but semantically empty JSON.

APIs and structure: Contains `{}`. It exercises the `_load_file_dict` check that rejects empty objects after successful JSON parsing.

Control flow and state: No executable behavior.

Dependencies and risks: The parser raises custom `NoValuesError`; tests depend on the exact empty-object path rather than invalid JSON.

Test signals: Expected message includes `returned empty object`.
