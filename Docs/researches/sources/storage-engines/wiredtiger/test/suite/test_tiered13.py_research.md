# sources/storage-engines/wiredtiger/test/suite/test_tiered13.py

## Purpose
`test_tiered13.py` verifies that importing tiered tables or tiered object files is rejected through all relevant import paths.

## Important APIs, Types, and Functions
The test class inherits `test_import_base` and `TieredConfigMixin`. It uses metadata cursors, file copying helpers, `shutil`, `wiredtiger.WiredTigerError`, and tiered connection setup for an import database.

## Control Flow
The test creates a tiered table, writes and force-flushes object 1, writes more data and checkpoints so object 2 exists, then extracts metadata for the current file object and table. After closing, it creates `IMPORT_DB`, opens it with tiered storage enabled, copies the object into several target names, builds import configurations with and without `file_metadata`, and asserts failures for table URI import, table URI plus tiered metadata, file URI import, file URI plus metadata, and renamed file plus metadata.

## State and Persistence Behavior
It uses real tiered object files and exported metadata to exercise import validation. The expected persistence rule is that tiered objects are not portable through generic import because their metadata and object lifecycle are tiered-managed.

## Dependencies and Integration Points
It integrates with WiredTiger import configuration, metadata export, tiered file-object metadata, and test import base helpers.

## Risks and Test Signals
Risks include accidentally allowing import with file metadata or returning misleading errors. Signals are expected `ENOENT`, `Operation not supported`, and incompatible file-metadata error messages.
