<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/bindings/java/src/main/com/apple/foundationdb/tuple/IterableComparator.java -->
# sources/storage-engines/foundationdb/bindings/java/src/main/com/apple/foundationdb/tuple/IterableComparator.java

## Purpose
`IterableComparator` compares iterable tuple items in the same order as FoundationDB tuple byte encodings.

## Important APIs, Types, And Functions
The class implements `Comparator<Iterable<?>>`; its only behavior is `compare`, which iterates both sides and delegates item ordering to `TupleUtil.compareItems`.

## Control Flow, State, And Persistence
Comparison proceeds element-wise until a non-zero item comparison or one iterable ends. A longer iterable sorts after its prefix. The comparator has no mutable state or persistence.

## Dependencies And Integration Points
`Tuple.compareTo` uses this comparator when packed bytes are unavailable or incomplete versionstamps make byte order unsafe. `TupleUtil` uses another instance for nested collection comparison.

## Risks And Test Signals
Risks include unsupported element types surfacing as `IllegalArgumentException`, iterator side effects, and consistency with packed tuple bytes. Tests should compare tuples, raw lists, nested lists, prefix cases, floats/NaN, UUIDs, strings with surrogate pairs, and byte arrays.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/bindings/java/src/main/com/apple/foundationdb/tuple/IterableComparator.java -->
