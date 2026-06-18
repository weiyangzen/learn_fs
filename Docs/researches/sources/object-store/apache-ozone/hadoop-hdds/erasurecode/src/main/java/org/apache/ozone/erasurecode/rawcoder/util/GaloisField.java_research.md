<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/erasurecode/src/main/java/org/apache/ozone/erasurecode/rawcoder/util/GaloisField.java -->
# sources/object-store/apache-ozone/hadoop-hdds/erasurecode/src/main/java/org/apache/ozone/erasurecode/rawcoder/util/GaloisField.java

## Purpose
`GaloisField` is a general GF utility for field arithmetic, Vandermonde solving, polynomial operations, substitution, remainders, and Gaussian elimination.

## Important APIs, Types, and Functions
It caches instances by field size/primitive polynomial, defaults to GF(256) with primitive polynomial 285, and exposes `getInstance`, `getFieldSize`, `getPrimitivePolynomial`, `add`, `multiply`, `divide`, `power`, several `solveVandermondeSystem` overloads, polynomial `multiply`, `remainder`, `add`, `substitute` overloads, and `gaussianElimination`.

## Control Flow
Construction builds log/power tables and multiplication/division tables. Bulk methods operate over byte arrays or ByteBuffers with absolute offsets. Vandermonde solving and remainder methods mutate provided arrays/buffers in place.

## State and Persistence Behavior
Field instances and arithmetic tables are cached statically. Most operation state is caller-provided and often mutated.

## Dependencies and Integration Points
`RSUtil.GF` uses the default instance for primitive powers and field-size validation. The class is also a reusable utility for older RS-style algorithms.

## Risks and Test Signals
Risks include reliance on Java `assert` for argument validation, in-place mutation surprises, divide-by-zero misuse, and ByteBuffer position/limit assumptions. Test signals include known arithmetic identities, polynomial operations, bulk substitution/remainder correctness, and RS coder round trips.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/erasurecode/src/main/java/org/apache/ozone/erasurecode/rawcoder/util/GaloisField.java -->
