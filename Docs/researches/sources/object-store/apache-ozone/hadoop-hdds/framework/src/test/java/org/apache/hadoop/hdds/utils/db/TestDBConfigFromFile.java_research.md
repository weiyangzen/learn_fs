<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/test/java/org/apache/hadoop/hdds/utils/db/TestDBConfigFromFile.java -->
# sources/object-store/apache-ozone/hadoop-hdds/framework/src/test/java/org/apache/hadoop/hdds/utils/db/TestDBConfigFromFile.java

Purpose: tests loading RocksDB DB and column-family options from `.ini` option files via `DBConfigFromFile`.

Important APIs/types/functions: `DBConfigFromFile.CONFIG_DIR`, `getOptionsFileNameFromDB`, `readDBOptionsFromFile`, `readCFOptionsFromFile`, RocksDB `DBOptions`, `ManagedColumnFamilyOptions`, `CompactionStyle`, and test resource `test.db.ini`.

Control flow: setup points the config-dir system property at a temp directory and copies the test `.ini` resource there; teardown clears the property. Tests read DB options from an existing file and assert option values, return null for missing/empty paths, throw for an empty option file, and read named column-family options with expected RocksDB settings.

State and persistence behavior: uses temp filesystem config files and a process-wide system property. RocksDB option objects hold native resources through managed wrappers.

Dependencies and integration points: integrates DB option-file naming, RocksDB option parsing, managed column-family options, and resource copying.

Risks: system property cleanup is important for test isolation. RocksDB option-file syntax and expected option values are version-sensitive.

Test signals: asserts DB options `maxManifestFileSize`, `keepLogFileNum`, `writableFileMaxBufferSize`; null for non-existent/empty paths; RocksDB exception text for empty file; and CF options including write buffer size, levels, blob file size, memtable factory, compaction style, and arena block size.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/test/java/org/apache/hadoop/hdds/utils/db/TestDBConfigFromFile.java -->
