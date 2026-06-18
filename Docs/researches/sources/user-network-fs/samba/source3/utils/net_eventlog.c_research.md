# sources/user-network-fs/samba/source3/utils/net_eventlog.c

Purpose: implements local `net eventlog` dump/import/export utilities for Windows `.evt` files and Samba eventlog TDB storage.

Important APIs/types/functions: `net_eventlog()` dispatches `dump`, `import`, and `export`. Dump loads and NDR-prints `EVENTLOG_EVT_FILE`; import converts `.evt` records to TDB records; export converts eventlog TDB content to `.evt`.

Control flow: dump/import use `file_load()` and NDR pull helpers. Import first parses `EVENTLOGHEADER`, rejects wrapped logs, parses full file, opens destination TDB, computes record count from header numbers, converts and pushes records. Export opens TDB, calls `evlog_convert_tdb_to_evt()`, and saves the blob.

State and persistence: import writes eventlog TDB records; export writes a caller-specified `.evt` file; dump is read-only.

Dependencies/integration: depends on `lib/eventlog/eventlog.h`, generated NDR eventlog parsers/printers, util file helpers, and local `net_run_function()` dispatch.

Risks: wrapped logs are unsupported. Record count assumes header and record array consistency. Import can partially write before a later failure. File paths are caller controlled.

Test signals: valid/invalid dump; import non-wrapped and wrapped logs; TDB record verification; export then re-dump; file permission errors; partial-write failure behavior.
