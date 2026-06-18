# sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/fs/SaveSpaceUsageToFile.java

## Purpose

`SaveSpaceUsageToFile` persists a cached used-space value and timestamp so startup can avoid expensive `du` scans when a recent value is available.

## Important APIs, Types, and Functions

`load()` returns `OptionalLong` when the file contains a non-expired value and timestamp. `save(SpaceUsageSource)` deletes the old file, reads `source.getUsedSpace()`, and writes `used epochMillis` if used is positive. The constructor requires a non-null file and positive expiry.

## Control Flow

Loading uses a UTF-8 `Scanner`, reading value first and time second. Expired, missing, or malformed-incomplete cache data returns empty. Saving writes the timestamp last, so truncated files are rejected on the next load.

## State and Persistence Behavior

The cache file is the durable state. It is advisory; write failures are logged and ignored.

## Dependencies and Integration Points

It implements `SpaceUsagePersistence` and is used by `DUFactory` and `DUOptimizedFactory`.

## Risks and Test Signals

Malformed numeric data other than missing tokens can still throw scanner/parse exceptions outside the explicit `FileNotFoundException` path. Tests should cover absent files, expired files, truncated files, positive save/load, zero usage skip, and write failure logging.
