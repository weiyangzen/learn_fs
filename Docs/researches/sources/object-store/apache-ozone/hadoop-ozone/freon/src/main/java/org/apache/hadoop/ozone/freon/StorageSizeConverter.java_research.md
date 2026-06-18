# sources/object-store/apache-ozone/hadoop-ozone/freon/src/main/java/org/apache/hadoop/ozone/freon/StorageSizeConverter.java

## Purpose
`StorageSizeConverter` is a picocli converter that turns command-line size strings into HDDS `StorageSize` values.

## Important APIs, Types, and Functions
The class implements `CommandLine.ITypeConverter<StorageSize>`. `STORAGE_SIZE_DESCRIPTION` is shared in option descriptions to tell users that units such as `GB`, `MB`, and `KB` are accepted and interpreted as binary units. `convert(String)` delegates to `StorageSize.parse(value, StorageUnit.BYTES)`.

## Control Flow
Picocli invokes `convert()` when parsing options annotated with `converter = StorageSizeConverter.class`.

## State and Persistence Behavior
The converter is stateless and has no persistence behavior.

## Dependencies and Integration Points
It integrates with Freon CLI classes that accept sizes, including `RandomKeyGenerator` and `RangeKeysGenerator`, and depends on HDDS `StorageSize` and `StorageUnit`.

## Risks and Edge Cases
Validation and error wording come from `StorageSize.parse()`. Callers should still consider semantic limits, such as multipart minimum part sizes or buffer interactions.

## Test Signals
No direct test in this subset covers the converter. It is indirectly exercised whenever picocli parses Freon size options.
