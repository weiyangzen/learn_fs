# sources/user-network-fs/samba/source3/torture/test_tdb_validate.c

## Purpose

`test_tdb_validate.c` is a small negative test for Samba's `tdb_validate` wrapper. It verifies that validation fails when the caller-supplied validation callback rejects a record, and that the failure is propagated to the caller.

## Important APIs, Types, and Functions

- `validate_fn`: callback passed to `tdb_validate`; it receives the TDB context, key, value, and private data, marks `struct tdb_validation_status->success` false, prints a trace line, and returns `-1`.
- `run_tdb_validate`: exported torture entry point that creates a temporary database, stores one record, invokes validation, and expects failure.
- `struct tdb_context`, `TDB_DATA`, `tdb_open`, `tdb_store`, `tdb_validate`, and `tdb_close` are the core TDB APIs.
- `struct tdb_validation_status` comes from `source3/lib/tdb_validate.h` and is used by the validation implementation's private data path.

## Control Flow

`run_tdb_validate` unlinks `tdb_validate.tdb`, creates a new exclusive read/write TDB with mode `0600`, stores a single key/value pair where both key and value are the local `"data"` buffer including its terminating NUL, then calls `tdb_validate(tdb, validate_fn)`. If `tdb_validate` returns `0`, the test reports that validation unexpectedly succeeded and fails. If `tdb_validate` returns nonzero, the function marks the result true, closes the database, unlinks the file, and returns success.

Every setup failure jumps to the shared cleanup block after printing with `perror` or `fprintf`.

## State and Persistence Behavior

The test creates a local temporary file named `tdb_validate.tdb` in the current working directory. It unlinks that file before opening to avoid stale state, and unlinks it again during cleanup. The only record stored is a small stack-buffer-backed `TDB_DATA` value copied into the database by `tdb_store`.

The validation callback mutates only the `tdb_validation_status` object passed by `tdb_validate` as private data. There is no long-lived in-memory state.

## Dependencies and Integration Points

This file integrates with the source3 torture harness through `source3/torture/proto.h`, with the public TDB library through `<tdb.h>`, and with Samba's validation wrapper through `source3/lib/tdb_validate.h`. It is designed to confirm that the wrapper honors callback failure rather than silently accepting corrupt or policy-rejected data.

## Risks and Edge Cases

- `tdb_close(tdb)` is called in the cleanup block even if `tdb_open` failed and `tdb` is `NULL`; this depends on the TDB close API tolerating a null pointer or on the test environment not hitting that path.
- The fixed filename can collide if multiple instances run in the same working directory.
- The callback's assignment to `state->success` assumes `tdb_validate` always passes a valid `struct tdb_validation_status` as private data.
- The test validates failure propagation, not detection of structural database corruption.

## Test Signals

Expected success is a nonzero return from `tdb_validate` after `validate_fn called` is printed. Unexpected signals include inability to create/store in the temporary TDB, `tdb_validate` returning success despite the callback returning `-1`, or cleanup problems caused by the fixed temporary filename.
