# sources/object-store/apache-ozone/hadoop-hdds/config/src/main/java/org/apache/hadoop/hdds/conf/StorageUnit.java

## Purpose
Enum defining binary storage units from bytes through exabytes and conversion helpers among them.

## Important APIs, Types, And Functions
Each unit implements conversion methods `toBytes`, `toKBs`, `toMBs`, `toGBs`, `toTBs`, `toPBs`, `toEBs`, `fromBytes`, suffix accessors, `getDefault`, and `toString`. Helpers use `BigDecimal` with scale 4.

## Control Flow
Converters multiply or divide by powers of 1024. `StorageSize.parse` iterates units in declared order, relying on `BYTES` being last so the `b` suffix does not preempt longer suffixes.

## State And Persistence
No mutable state; constants encode unit metadata and conversion ratios.

## Dependencies And Integration Points
Used by `Config`, `ConfigType.SIZE`, `ConfigurationSource`, `ConfigurationTarget`, and `StorageSize`.

## Risks
Double output plus 4-decimal rounding can lose precision for very large values. Comments mention overflow behavior but `BigDecimal.doubleValue()` may still produce infinity for enormous values. Enum order is a correctness contract.

## Test Signals
Tests should cover conversion matrix, suffix names, byte overlap ordering, large values, fractional values, and round-trip parse/format with `StorageSize`.
