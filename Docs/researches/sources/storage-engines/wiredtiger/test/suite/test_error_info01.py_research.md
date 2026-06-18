# sources/storage-engines/wiredtiger/test/suite/test_error_info01.py

## Purpose

Validates `WT_SESSION.get_last_error()` state for ordinary success, background compaction reconfiguration errors, and two drop-related `EBUSY` reasons.

## Important APIs, Types, and Functions

`test_error_info01` inherits `error_info_util` and `compact_util`. Helpers trigger success, `WT_BACKGROUND_COMPACT_ALREADY_RUNNING`, `WT_UNCOMMITTED_DATA`, and `WT_DIRTY_DATA`; test methods assert POSIX errno, WiredTiger sub-level reason, and message.

## Control Flow

The success path creates/inserts/searches a table. Error paths start background compaction, attempt forbidden compact reconfiguration, attempt drop with an open uncommitted transaction, or commit dirty data and drop before checkpoint. Alternating/doubling tests call those methods repeatedly to ensure the last-error slot updates after every API call.

## State and Persistence Behavior

State lives in the session's last-error fields plus table transactional state. Cleanup rolls back or checkpoints/drops as needed to keep the test home usable.

## Dependencies and Integration Points

Depends on `wiredtiger`, `errno`, `time`, `open_cursor`, `error_info_util.assert_error_equal`, and background compact utilities.

## Risks and Maintenance Signals

Dirty-data timing uses `sleep(1)` to let oldest id accounting move. Reusing test methods inside alternating tests means those methods must fully clean their data state.

## Test Signals

Signals are exact major error code, sub error code, and human-readable reason for success, background compaction, uncommitted data, and dirty data, across repeated transitions.
