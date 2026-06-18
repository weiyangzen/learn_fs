# sources/storage-engines/wiredtiger/test/suite/test_dictionary04.py

Purpose: combines the dictionary/RLE scenario with timestamp time-window metadata to verify the encodings compose correctly.

Important APIs and control flow: creates a dictionary-compressed file for row-store and VLCS scenarios, pins timestamps, writes two unique values, then writes keys 3 through 9 with the first value in a timestamped transaction. Checkpoint triggers reconciliation and the test reads `stat.dsrc.rec_dictionary`.

State and persistence: checkpointed cells may include time windows and, for VLCS, RLE metadata. The dictionary statistic is the behavioral signal.

Dependencies and integration: uses `simple_key`, `make_scenarios`, timestamps, and WiredTiger statistics.

Risks and test signals: row-store expects seven dictionary reuses; VLCS expects one because RLE compresses adjacent repeated values. It catches regressions in dictionary eligibility when both RLE and time windows are present.
