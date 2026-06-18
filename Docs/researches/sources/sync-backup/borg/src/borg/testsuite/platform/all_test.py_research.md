# sources/sync-backup/borg/src/borg/testsuite/platform/all_test.py

Purpose: tests platform-neutral functions: string display width and `SyncFile` file-object behavior.

Important APIs and control flow: `swidth` is checked for ASCII, CJK, and mixed strings. `SyncFile` is opened on a temp path in binary mode, writes data, uses `tell`, `seek`, and `read`, then verifies final bytes. Another test closes a `SyncFile` twice to require idempotent close.

State and persistence: writes temporary files and flushes through `SyncFile`.

Dependencies and integration points: depends on `borg.platform.swidth` and `SyncFile`. These support terminal formatting and durable metadata writes across platforms.

Risks: display width depends on platform/wcwidth implementation. `SyncFile` must expose enough file methods for wrapper code and tolerate double close.

Test signals: exact widths, seek/tell positions, persisted bytes, and no exception on repeated close.
