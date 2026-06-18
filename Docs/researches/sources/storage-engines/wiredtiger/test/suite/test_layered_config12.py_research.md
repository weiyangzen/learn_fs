# sources/storage-engines/wiredtiger/test/suite/test_layered_config12.py

Purpose: validates unsupported disaggregated/layered configurations return clear errors: read-only disaggregated connections and custom collators on layered tables.

Important APIs/types/functions: uses `conn_extensions` to load `collators/reverse` plus disagg extensions, `wiredtiger_open`, `assertRaisesWithMessage`, `session.create`, `session.open_cursor`, and table drop cleanup.

Control flow: `test_readonly` closes the normal connection and attempts to open the home with `readonly=true` and disaggregated leader config, expecting an error that disaggregated storage is not supported with read-only connections, then reopens normally. `test_reverse_collator` creates a layered table with `collator=reverse`, expects cursor open to fail with `layered tables do not support custom collators`, then drops the table so layered verify teardown does not fail on the unsupported configuration.

State and persistence behavior: read-only open should not create usable disaggregated state. The collator test writes metadata successfully but rejects dhandle/cursor open, then removes the metadata.

Dependencies/integration points: connection open validation, collator extension loading, layered dhandle open checks, and teardown verify.

Risks: behavior intentionally permits create but rejects cursor for collator case; if validation moves earlier, test expectations must change.

Test signals: pass means these unsupported paths produce deterministic user-facing errors and leave teardown clean.
