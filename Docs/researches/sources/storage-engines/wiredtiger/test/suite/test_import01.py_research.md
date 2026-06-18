# sources/storage-engines/wiredtiger/test/suite/test_import01.py

Purpose: provides the shared file-import helper base and tests successful file import both into a different database home and back into the same home after dropping the file object.

Important APIs and functions: `test_import_base` defines `update`, `delete`, `check_record`, `check`, `config_compare`, `strip_subconfig`, `populate`, and `copy_file`. `test_import01` sets binary keys/values, timestamp list, and `create_config='allocation_size=512,key_format=u,value_format=u'`.

Control flow: `test_file_import` creates a file, writes/checkpoints two batches, exports metadata via `metadata:` cursor, closes, creates `IMPORT_DB`, populates unrelated files, advances oldest timestamp, copies the source file, imports with `import=(enabled,repair=false,file_metadata=(...))`, verifies, compares metadata excluding IDs/checkpoints, appends remaining data, and checkpoints. `test_file_import_dropped_file` backs up the file, drops it, copies it back, imports into the same database, and validates.

State and persistence behavior: the test depends on checkpointed on-disk file state and exported metadata. Oldest timestamp must be advanced beyond imported timestamps so import timestamp validation succeeds.

Dependencies and integration points: integrates metadata cursors, file copying, `session.create` import config, `verifyUntilSuccess`, and binary key/value formats. Later import tests depend on `test_import_base`.

Risks and edge cases: metadata comparison strips only IDs and checkpoint subconfigs; future metadata fields may require updates. Random table names in `populate` make auxiliary data varied but not deterministic.

Test signals: imported contents match original checkpointed keys, metadata is equivalent after stripping unique fields, and new post-import writes/readbacks succeed.
