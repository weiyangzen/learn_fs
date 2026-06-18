## sources/user-network-fs/gcsfuse/perfmetrics/scripts/fio/testdata/empty_file.json

Purpose: Negative parser fixture for a zero-byte FIO output file.

APIs and structure: Contains no JSON content. It is used to verify `_load_file_dict` surfaces `json.load` `ValueError` for empty files.

Control flow and state: No runtime behavior.

Dependencies and risks: The file intentionally must remain empty. Adding whitespace or `{}` would test a different error path.

Test signals: `fio_metrics_test` expects `ValueError` when loading this fixture.
