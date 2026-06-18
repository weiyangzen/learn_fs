# sources/storage-engines/rocksdb/java/src/test/java/org/rocksdb/InfoLogLevelTest.java

## Purpose

Tests info log level behavior for Java options and enum mapping.

## Important APIs, control flow, and dependencies

The tests open DBs with default logging and with `InfoLogLevel.FATAL_LEVEL` through `Options` and `DBOptions`, flush data, and inspect the RocksDB `LOG` file after stripping headers. It also verifies invalid byte mapping and `valueOf`.

## State, persistence, risks, and test signals

The persisted artifact is the DB log file in the temporary DB directory. Risks include platform-specific path separators, log header filtering, default logging changes, and enum byte drift. Signals are nonempty log body at default level, empty log body at fatal level, and expected enum/exception behavior.
