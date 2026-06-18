<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_schema08.py -->
# sources/storage-engines/wiredtiger/test/suite/test_schema08.py

Purpose: validates recovery behavior for schema operations by truncating log copies at each schema log record boundary and running recovery/listing on the partial homes.

Important APIs/types/functions: `test_schema08` mixes `TieredConfigMixin`, `suite_subprocess`, log cursors, `session.log_flush`, `session.alter`, `session.drop`, checkpoint, `runWt`, and filesystem copying/truncation via `os` and `shutil`. Scenarios cover file/table URIs, column groups, indexes, no-op/alter/drop operations, and optional checkpoints.

Control flow: create a main object, optionally checkpoint, create a column group or index subobject, optionally alter or drop the schema, walk the log cursor to collect whole-record LSN offsets, copy the home once per LSN, truncate `WiredTigerLog.0000000001` to that offset, then run `wt -R -h <backup> list -v`.

State and persistence behavior: state is persisted in the log and metadata files; each backup represents recovery before a selected record. Tiered scenarios skip backup/recovery truncation because copied local logs are not equivalent.

Dependencies/integration points: covers schema logging, metadata recovery, log cursor record semantics, external `wt`, and backup-like copies. Risks include one-log-file assumption, platform lock-file exclusions, and broad expected error handling; signals are successful recovery/listing for all truncated states.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_schema08.py -->
