<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/hooks/hook_timestamp.py -->
# sources/storage-engines/wiredtiger/test/suite/hooks/hook_timestamp.py

Purpose: Hook that injects automatic timestamp behavior into dataset-based tests by providing a timestamp generator and tracking explicit transaction boundaries.

Important APIs and types: Replacements `session_begin_transaction_replace`, `session_commit_transaction_replace`, `session_rollback_transaction_replace`, helper `make_dataset_names`, `TimestampHookCreator`, and `TimestampPlatformAPI`.

Control flow: On initialization, the hook discovers dataset class names from `wtdataset`. It skips tests whose module globals do not include a dataset type because the hook only affects dataset wrappers. `setup_hooks` replaces session transaction methods to call originals and maintain `session._has_transaction`. `TimestampPlatformAPI.setUp` creates a new `WiredTigerTimeStamp` for each testcase, which `wtdataset` uses for timestamped cursors.

State and persistence behavior: Per-testcase timestamp generator state increments as dataset cursor operations commit or timestamp transactions. Per-session `_has_transaction` prevents timestamped cursors from opening nested transactions when the test already has one active.

Dependencies and integration points: Depends on `wttimestamp`, `wtdataset`, hook platform API `getTimestamp`, and `wttest.prevent("timestamp")` for tests with custom timestamp logic.

Risks: Skip detection scans module globals and can miss indirect dataset use. Global replacement of transaction APIs affects all sessions in the process. If a transaction method raises before flag update, `_has_transaction` may become stale.

Test signals: Dataset tests should pass under automatic commit timestamps, custom timestamp tests should be skipped by `prevent`, and no nested-transaction errors should occur.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/hooks/hook_timestamp.py -->
