## sources/storage-engines/pebble/sstable/block/kv.go

Purpose: Defines the one-byte value prefix stored with block values to distinguish in-place values, SSTable value-block handles, blob handles, same-prefix optimization, and short attributes.

Important APIs/types/functions: `ValuePrefix`, bit masks/constants for value kind, `IsInPlaceValue`, `IsValueBlockHandle`, `IsBlobValueHandle`, `SetHasSamePrefix`, `ShortAttribute`, `ValueBlockHandlePrefix`, `InPlaceValuePrefix`, `BlobValueHandlePrefix`, and `GetInternalValueForPrefixAndValueHandler`.

Control flow: Methods are bit tests and constructors. The two high bits encode value kind; bit `0x20` records whether a SET has the same key prefix as the previous SET in the block; low three bits encode `base.ShortAttribute` for non-in-place values.

State and persistence behavior: This prefix is part of encoded block values and therefore format-sensitive. The same-prefix bit supports block/value-block layout optimizations and must be interpreted consistently by readers.

Dependencies and integration points: Depends on `internal/base` for `ShortAttribute` and `InternalValue`. Used by row/column block writers and iterators, value-block handle decoding, blob handle decoding, and lazy value retrieval.

Risks: `ShortAttribute` is documented as requiring non-in-place values, but not enforced. Only three bits are available for user-defined attributes. Reserved/invalid combinations are not rejected here.

Test signals: `kv_test.go` covers constructors and accessors for in-place, value-block, and blob prefixes with same-prefix flags and attributes.
