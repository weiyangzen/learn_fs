# sources/object-store/apache-ozone/hadoop-hdds/framework/src/test/java/org/apache/hadoop/hdds/fs/TestSaveSpaceUsageToFile.java

## Purpose

This class tests file-backed space-usage persistence, including valid saves, invalid values, expiry, missing data, garbage content, missing files, and overwrite behavior.

## Important APIs, Types, And Functions

The subject is `SaveSpaceUsageToFile`. Tests call `save(SpaceUsageSource)` and `load()`. Helpers include `saveToFile(String)`, `MockSpaceUsageSource.fixed`, and `GenericTestUtils.waitFor`.

## Control Flow

Each test sets a temp `space_usage.txt` path, constructs persistence with either a long or short expiry, writes through subject or manually, then loads and asserts `OptionalLong` presence/value and file existence.

## State And Persistence

State is actual file content in a temp directory. A valid save writes used-space and timestamp. Invalid zero-used source does not create a file. Expired, malformed, time-missing, and absent files return empty values.

## Dependencies And Integration Points

It integrates with Commons IO file writing, UTF-8 encoding, Java `Instant`/`Duration`, `SpaceUsagePersistence`, and `SpaceUsageSource`.

## Risks

Expiry tests rely on wall-clock timing and `waitFor`, so slow or clock-skewed environments can be flaky. The test assumes the invalid source with used zero should not persist.

## Test Signals

Signals are file creation for valid usage, empty loads for invalid/expired/missing/garbage data, and replacement of existing file content with the latest valid used-space value.
