# sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/ozone/om/TestObjectStoreWithFSO.java

Purpose: This abstract non-HA integration suite validates object-store and filesystem behavior for `FILE_SYSTEM_OPTIMIZED` buckets. It covers FSO key creation, open-file table movement, bucket emptiness with intermediate directories, lookup visibility for open/deleted keys, recursive key listing, path normalization, key renames, and bucket layout creation defaults.

Important APIs and types: The file uses `MiniOzoneCluster`, `OzoneFileSystem`, `FileSystem`, `ObjectStore`, `OzoneVolume`, `OzoneBucket`, `OzoneOutputStream`, `KeyOutputStream`, `OMMetadataManager`, `Table<String, OmKeyInfo>`, `OmDirectoryInfo`, `BucketLayout.FILE_SYSTEM_OPTIMIZED`, `OmUtils.normalizeKey`, `OMException` result codes `KEY_NOT_FOUND` and `KEY_ALREADY_EXISTS`, and config `OZONE_FS_ITERATE_BATCH_SIZE`.

Control flow: Setup creates an FSO volume/bucket, configures `fs.defaultFS` to the Ozone URI, and cleans root contents after each test. Key-creation and lookup tests create nested keys, inspect directory table parent object IDs, verify rows appear in open-file tables while streams are open, then close streams and verify rows move to the key table. Listing tests build a multi-level tree and compare depth-first listings for root, prefixes, previous-key boundaries, not-normalized paths, and direct bucket-level keys. Rename tests move keys to bucket level, across subdirectories, and into existing-key conflicts.

State and persistence behavior: The suite directly checks OM FSO metadata tables: directory table rows, open-key table rows keyed by parent ID and client ID, final key table rows, and bucket emptiness after file and directory deletion. It also validates filesystem-visible data by reading through both `OzoneBucket.readKey` and `OzoneFileSystem.open`.

Dependencies and integration points: It integrates Ozone object-store APIs, FSO metadata manager key generation, Hadoop filesystem URI handling, key stream client IDs, batch listing, path normalization, and recursive cleanup.

Risks: Tests rely on async DB cleanup for open-key rows and use `GenericTestUtils.waitFor`. Direct parent-object-ID assertions are sensitive to FSO DB key format changes. Root cleanup assumes all created paths can be recursively removed through the filesystem API.

Test signals: Signals include expected open-key and key-table presence/absence, correct parent object IDs and filenames, `KEY_NOT_FOUND` for open/deleted/renamed keys, bucket deletion failure until intermediate directories are removed, exact listing order for the constructed tree, normalized prefix behavior, successful reads through both APIs, and `KEY_ALREADY_EXISTS` on conflicting rename.
