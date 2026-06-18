# File Research: sources/windows/reactos/drivers/filesystems/udfs/udf_info/osta_misc.h

## Purpose
Defines OSTA/UDF-specific packed metadata structures, identifiers, partition-map types, revision-related suffixes, VAT/sparing layouts, reserved names, and extent flag masks used by the UDFS implementation.

## Key Elements
- Declares `LogicalVolIntegrityDescImpUse` and `ImpUseVolDescImpUse`, which are consumed by mount logic for UDF revision limits, file/dir counts, volume identity, and implementation-use metadata.
- Defines type 2 partition map variants: generic UDF map, virtual partition map, sparable partition map, and UDF 2.5 metadata partition map.
- Provides partition type constants such as `UDF_TYPE1_MAP15`, `UDF_VIRTUAL_MAP15`, `UDF_VIRTUAL_MAP20`, `UDF_SPARABLE_MAP15`, and `UDF_METADATA_MAP25`.
- Defines VAT 1.5 and VAT 2.0 layouts, sparing entries/tables, domain/UDF/implementation identifier suffixes, entity identifier strings, OS class/id constants, name/path/label limits, and reserved UDF filenames/system stream names.
- Defines `UDF_EXTENT_LENGTH_MASK`, `UDF_EXTENT_FLAG_MASK`, and `UDF_EXTENT_FLAG_ERASED`, which are central to `extent.cpp` because extent state is encoded in the high bits of `extLength`.

## Dependencies
Includes `ecma_167.h` and uses packed layout via `#pragma pack(push, 1)`, so these definitions are intended to match on-disk UDF structures byte-for-byte. It also depends on `VER_STR_PRODUCT_NAME` for the developer identifier string.

## Behavior/Risks
This header is structural rather than executable, but layout correctness is critical: packing, fixed-size arrays, and identifier strings directly affect disk parsing and serialization. Any change to these definitions can break compatibility with UDF media, especially VAT, sparable, metadata partition, and implementation-use descriptors.
