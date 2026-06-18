# sources/storage-engines/rocksdb/java/src/test/java/org/rocksdb/util/SizeUnitTest.java

Purpose: Simple unit test for RocksJava `SizeUnit` constants.

Important APIs/types/functions: `SizeUnit.KB`, `MB`, `GB`, `TB`.

Control flow and state: asserts each larger unit equals the previous unit multiplied by 1024, starting from `COMPUTATION_UNIT`.

State and persistence behavior: none.

Dependencies and integration points: validates constants used by Java tests/configuration examples for byte sizes.

Risks: only checks relative values, not overflow boundaries or string parsing.

Test signals: basic regression coverage for binary size unit constants.
