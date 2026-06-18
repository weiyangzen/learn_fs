# sources/storage-engines/wiredtiger/test/suite/test_util21.py

## Purpose

`test_util21.py` ensures `wt dump file:WiredTigerHS.wt` can dump obsolete history-store data and that advancing oldest timestamp plus checkpoint does not unexpectedly remove clean obsolete history-store content.

## Important APIs, Types, and Functions

The class defines `conn_config='cache_size=50MB'`, `add_data_with_timestamp`, and `test_dump_obsolete_data`. It uses transactions with commit timestamps, connection timestamp setting, checkpoint, `runWt`, and `helper.compare_files`.

## Control Flow

The test creates a table, sets oldest timestamp, writes four timestamped value generations, checkpoints, sets stable timestamp to protect data across utility reopen, dumps the history store, advances oldest timestamp to 6, checkpoints again, dumps the history store again, and compares the dump files.

## State and Persistence Behavior

Persistent state includes table updates at timestamps 2, 3, 5, and 7 and resulting history-store records in `WiredTigerHS.wt`. Checkpoints make pages clean and stable timestamp protects state during `wt dump`.

## Dependencies and Integration Points

Integrates timestamp management, history store cleanup rules, checkpoints, and `wt dump` of an internal file.

## Risks and Edge Cases

The test assumes clean pages are not rewritten/cleaned during the second checkpoint. It is sensitive to history-store format and cleanup policy changes.

## Test Signals

The key signal is byte-equivalent dump output before and after oldest timestamp advancement.
