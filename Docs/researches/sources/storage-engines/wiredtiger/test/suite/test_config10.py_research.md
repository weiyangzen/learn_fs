<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_config10.py -->
# sources/storage-engines/wiredtiger/test/suite/test_config10.py

Purpose: validates startup behavior when the `WiredTiger` version file is missing or empty, with and without salvage.

Important APIs and control flow: tests close the default connection, remove or truncate the `WiredTiger` file, and either expect a corruption/salvage-needed error, expect a stdout warning for an empty file, or reopen with `salvage=true` and assert the file is repopulated.

State, persistence, and dependencies: the central persistent object is the WiredTiger version file in the home. Dependencies are `os.remove`, `os.stat`, `wiredtiger_open`, `setUpConnectionOpen`, stdout pattern capture, and salvage startup logic.

Integration points: targets database-home bootstrap, version-file validation, corruption reporting, and salvage recovery path.

Risks and test signals: error text and stdout wording are part of the test surface. Pass signals are correct refusal of missing file without salvage, warning/recovery for empty file, and non-empty recreated version file with salvage.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_config10.py -->
