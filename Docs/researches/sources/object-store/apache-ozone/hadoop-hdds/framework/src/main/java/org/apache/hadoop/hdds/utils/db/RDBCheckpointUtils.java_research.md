# sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/utils/db/RDBCheckpointUtils.java

## Purpose
`RDBCheckpointUtils` contains polling helpers for waiting until a checkpoint directory appears after RocksDB checkpoint creation.

## Important APIs and Types
`waitForCheckpointDirectoryExist(File, Duration)` polls `file.exists()` every 100 ms until the supplied timeout. The overload without timeout uses a 20 second maximum.

## Control Flow and State
The utility delegates polling to `RatisHelper.attemptUntilTrue`. If the directory is not observed before timeout, it logs an informational message and returns false.

## Persistence, Dependencies, and Integration
There is no persistence. It depends on Java `File`, `Duration`, Ratis helper polling, and SLF4J. `RDBCheckpointManager` calls it after checkpoint creation.

## Risks and Test Signals
The no-timeout overload declares `IOException` but does not throw directly. A false result is not propagated as an exception by the manager. Tests should cover immediate success, delayed success, timeout logging, custom timeout, and interrupted/polling behavior through `RatisHelper`.
