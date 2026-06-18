# sources/storage-engines/wiredtiger/test/suite/test_util03.py

## Purpose
`test_util03.py` tests `wt create` for ordinary creation and import-style creation after preserving a dropped file.

## Important APIs, Types, and Functions
It defines `test_util03.test_create_process` over key/value format scenarios and `test_util03_import.test_create_process_import` over file-metadata and repair import modes. It uses `runWt(['create', '-c', ...])`, metadata cursors, `session.drop(remove_files=false)`, and import config.

## Control Flow
The ordinary create test runs the `wt create` command, opens the table, checks cursor key/value formats, and verifies the table is empty. The import test creates/populates/checkpoints a file, saves its file metadata, drops metadata while retaining files, verifies open fails, then recreates with `import=(...)` and reads values.

## State and Persistence Behavior
The import path preserves underlying `.wt` files while removing and reconstructing metadata. Data must remain readable after import.

## Dependencies and Integration Points
Depends on the external `wt create` utility, metadata cursor access, import/repair config, and file retention behavior.

## Risks and Edge Cases
Import metadata must match the preserved file; repair mode has looser expectations. Incorrect config could make a retained file unreadable.

## Test Signals
Cursor formats match requested formats, ordinary tables are empty, dropped files cannot open before import, and imported records read correctly.
