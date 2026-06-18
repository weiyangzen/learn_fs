# sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/hdds/utils/db/IteratorType.java

## Purpose
Describes whether a DB iterator should read keys, values, both, or neither.

## Important APIs, Types, And Functions
Enum constants are `NEITHER`, `KEY_ONLY`, `VALUE_ONLY`, and `KEY_AND_VALUE`, each with a bit mask. Methods `readKey()` and `readValue()` inspect the mask.

## Control Flow
The two query methods use bitwise comparison against `KEY_ONLY.mask` and `VALUE_ONLY.mask`.

## State And Persistence
Enum constants are immutable; there is no persistence.

## Dependencies And Integration Points
Intended for table iteration APIs where avoiding unused key/value decoding saves IO and CPU.

## Risks
Adding new mask values must preserve bit semantics. Callers must not assume ordinal values.

## Test Signals
Simple enum tests should assert key/value booleans for all four constants and any DB iterator behavior that uses them.
