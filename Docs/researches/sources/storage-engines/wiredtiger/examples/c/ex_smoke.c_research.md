# sources/storage-engines/wiredtiger/examples/c/ex_smoke.c

Purpose: standalone smoke test proving headers and libraries link without the example test utility layer.

Important APIs and control flow: includes only standard headers and `wiredtiger.h`. `main` removes and recreates `WT_HOME` via `system`, opens WiredTiger with `create`, closes the connection, and reports errors with `wiredtiger_strerror`.

State and persistence: deletes and recreates a local `WT_HOME`; creates basic WiredTiger metadata; no user tables are written.

Dependencies and integration: intentionally avoids `test_util.h` so it validates a minimal external-client build. CMake marks it POSIX-dependent because it shells out to `rm`/`mkdir`.

Risks: destructive `rm -rf WT_HOME` is safe only in the example's working directory. It does not validate sessions, schema, or cursor APIs.

Test signals: successful compile/link/run establishes basic include/library linkage and connection lifecycle.
