# sources/storage-engines/rocksdb/java/src/test/java/org/rocksdb/FlushOptionsTest.java

## Purpose

Accessor coverage for `FlushOptions`.

## Important APIs, control flow, and dependencies

The tests round-trip `waitForFlush` and `allowWriteStall` on a native `FlushOptions` object.

## State, persistence, risks, and test signals

No DB state is created. These options affect memtable persistence in flush operations elsewhere. Risks are default drift and boolean setter binding errors. Signals are expected defaults and changed getter values.
