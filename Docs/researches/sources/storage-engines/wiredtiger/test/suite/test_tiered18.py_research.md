# sources/storage-engines/wiredtiger/test/suite/test_tiered18.py

## Purpose
`test_tiered18.py` tests schema metadata for tiered shared tables, where active local data and shared tiered data are represented by separate colgroups/files.

## Important APIs, Types, and Functions
The class uses `TieredConfigMixin`, `get_shared_conn_config`, and `metadata:create` cursors. `check_metadata` accepts exact or comma-continued metadata substrings so it can validate nested config like `log=(enabled=true,...)`.

## Control Flow
The currently active `test_tiered_shared` creates a table with `tiered_storage=(shared=true)`, then checks metadata for the table URI, active colgroup pointing to a local `file:` URI, shared colgroup pointing to a `tiered:` URI, and log configuration on both file and tiered entries. Several related default/shared-false/alter/drop checks are present but commented out under a FIXME.

## State and Persistence Behavior
The test validates metadata shape rather than data contents. Shared tiered tables persist as a table with active and shared colgroups, each linked to the expected underlying file/tiered data source.

## Dependencies and Integration Points
It integrates with shared tiered storage connection setup, schema create metadata generation, colgroup metadata, file metadata, and tiered metadata.

## Risks and Test Signals
The risk is wrong schema decomposition for shared tiered tables. Signals are required metadata links and log settings for active and shared components.
