# sources/storage-engines/foundationdb/contrib/local_cluster/lib/__init__.py

## Purpose
`lib/__init__.py` initializes logging for the local-cluster helper package.

## Important APIs, Types, And Functions
`_setup_logs()` obtains the package logger, clears handlers, constructs a timestamped formatter, attaches a stderr stream handler, and runs immediately at import time.

## Control Flow
Importing `lib` executes `_setup_logs`, which mutates the logger configuration for the package module name.

## State And Persistence Behavior
The only state change is process-local logging handler configuration. No files or cluster state are touched.

## Dependencies And Integration Points
It depends on `logging` and `sys`. Other modules under `lib` get named loggers and can inherit or coexist with this handler setup; top-level scripts sometimes add their own handlers to the `"lib"` logger.

## Risks And Edge Cases
Running logging setup at import time can surprise embedding applications and may interact with handlers added later by `binding_test.py` or `local_cluster.py`. It configures only `__name__`, not necessarily all child loggers.

## Test Signals
Tests can import the package and assert stderr handler presence and formatter shape, while checking repeated imports do not duplicate handlers.
