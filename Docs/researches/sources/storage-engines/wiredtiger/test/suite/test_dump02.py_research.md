# sources/storage-engines/wiredtiger/test/suite/test_dump02.py

Purpose: tests key filtering and lower/upper bound options in `wt dump`.

Important APIs and control flow: populates `table:test_dump` with byte-array keys `key1` through `key99`. `get_num_data_lines_from_dump` finds the `Data\n` header and counts data lines. Test cases run full dump, exact key `-k`, nearest `-k ... -n`, lower bound `-l`, upper bound `-u`, and combined bounds.

State and persistence: output file `dump.out` is overwritten for each utility invocation. Each record contributes two data lines, key and value.

Dependencies and integration: uses `suite_subprocess`, `wt dump`, and file parsing.

Risks and test signals: expected line counts encode lexicographic key ordering, including surprising string ranges such as `key6` through `key9` with lower bound `key50`. Failures indicate bound or nearest-key semantics changed.
