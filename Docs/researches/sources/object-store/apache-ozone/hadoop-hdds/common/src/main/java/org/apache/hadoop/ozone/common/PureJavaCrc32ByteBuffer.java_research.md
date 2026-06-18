# sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/ozone/common/PureJavaCrc32ByteBuffer.java

## Purpose

`PureJavaCrc32ByteBuffer` is a static utility retaining the precomputed table-backed `mod(long)` helper for CRC-32. Earlier checksum update methods have been removed; production and tests now use this class only for polynomial modular reduction.

## APIs and control flow

The class is non-instantiable and exposes only `mod(long x)`. The method splits the low 32 bits into bytes, uses four table slices offset by `0x000`, `0x100`, `0x200`, and `0x300`, XORs those lookups, and combines them with the high 32 bits. The table is generated for the CRC-32 polynomial `0xEDB88320`.

## State, dependencies, and integration

State is a large immutable static lookup table. There are no external dependencies beyond Java. It integrates with checksum combination or comparison logic that needs CRC polynomial arithmetic without an object-oriented checksum updater.

## Risks and test signals

The lookup table is opaque and easy to break with mechanical edits. Tests should compare `mod(long)` against known CRC-32 polynomial arithmetic vectors, especially values that exercise each byte lookup and high-bit behavior. Performance tests can confirm the table path remains allocation-free.
