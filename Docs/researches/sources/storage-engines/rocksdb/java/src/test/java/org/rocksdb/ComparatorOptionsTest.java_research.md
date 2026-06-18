# sources/storage-engines/rocksdb/java/src/test/java/org/rocksdb/ComparatorOptionsTest.java

## Purpose

Tests Java comparator option settings that affect Java comparator callback buffering.

## Important APIs, control flow, and dependencies

The suite uses `ComparatorOptions`, `ReusedSynchronisationType`, `setUseDirectBuffer`, and `setMaxReusedBufferSize`. It verifies reused synchronization mode transitions, direct-buffer toggling, and positive/negative buffer-size values.

## State, persistence, risks, and test signals

No DB is opened. The key state is native comparator option storage used later by `AbstractComparator` implementations. Risks include incorrect enum storage and buffer option defaults affecting comparator correctness or callback performance. Signals are getter equality and known defaults.
