<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/fops/fops_file.c -->
# sources/storage-engines/wiredtiger/test/fops/fops_file.c

Purpose: implements the individual WiredTiger operations used by the fops concurrency stress test.

Important APIs: `obj_bulk()`, `obj_bulk_unique(force)`, `obj_cursor()`, `obj_create()`, `obj_create_unique(force)`, `obj_drop(force)`, `obj_checkpoint()`, and `obj_verify()` each open a session, optionally wrap operations in a user transaction, and tolerate expected races such as `EEXIST`, `ENOENT`, `EBUSY`, and selected `EINVAL` results. Unique object functions use a global `uid` protected by `single` rwlock to create names like `<uri>.<uid>`.

Control flow: operations intentionally race on a shared `uri` or short-lived unique URIs. Bulk functions create/open bulk cursors and close them; unique variants drop the object afterward, retrying `EBUSY`. Drop rolls back transactions when expected race errors occurred. Forced checkpoint tolerates busy/missing object races.

State and persistence: creates, drops, verifies, and checkpoints WiredTiger objects in the current test home. Unique object state is transient; shared object may appear/disappear concurrently.

Dependencies and integration: uses globals and prototypes from `thread.h`, WiredTiger session/cursor APIs, pthread lock, and test utility checks.

Risks and test signals: the test intentionally accepts a narrow set of race errors; any other return is fatal. A format string in `obj_bulk_unique` passes `"new_uri"` instead of the variable, weakening diagnostics. Transactions can fail with `EINVAL` under concurrent metadata races and are tolerated in defined places.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/fops/fops_file.c -->
