# sources/storage-engines/sqlite/ext/jni/src/org/sqlite/jni/capi/ResultCode.java

## Purpose
Enum mapping SQLite core and extended integer result codes to named Java values for higher-level code.

## Important APIs, Types, And Functions
Each enum entry stores public final `int value`, initialized from `CApi` constants. `getEntryForInt(int rc)` looks up a result code through nested `ResultCodeMap`, which stores a static `HashMap<Integer, ResultCode>`.

## Control Flow
Each enum constructor inserts itself into the map. Lookup returns the enum value or null when no entry exists.

## State And Persistence Behavior
State is process-local static enum/map data initialized at class load. No persistence.

## Dependencies And Integration Points
Depends on `CApi` constants, which require native library initialization for version-related constants but result code constants are Java static finals. Useful for wrappers and diagnostics that want names instead of raw integers.

## Risks And Edge Cases
It only includes codes listed at compile time; new SQLite extended codes return null until updated. Static initialization order is handled by the nested map indirection.

## Test Signals
Assert every enum maps back from its integer value, representative core/extended code lookups, and null for unknown integers.
