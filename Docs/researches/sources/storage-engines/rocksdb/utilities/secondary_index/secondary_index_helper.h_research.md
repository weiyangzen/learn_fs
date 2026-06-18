# sources/storage-engines/rocksdb/utilities/secondary_index/secondary_index_helper.h

Purpose: provides conversion helpers for secondary-index APIs that accept either borrowed `Slice` or owned `std::string` in `std::variant`.

Important APIs/types: `SecondaryIndexHelper::AsSlice()` visits the variant and returns a `Slice` view. `AsString()` returns an owned `std::string`, copying a `Slice` or returning the existing string.

Control flow and state: no persistent state; functions are pure variant visitors. `AsSlice()` relies on the caller preserving variant lifetime when the active alternative is `std::string`.

Dependencies and integration: uses RocksDB `Slice`, namespace headers, and `util/overload.h`. It is used by `SecondaryIndexMixin`, `SecondaryIndexIterator`, and `SimpleSecondaryIndex`.

Risks and test signals: misuse of a returned `Slice` after the variant/string dies would dangle. The helper centralizes conversions, reducing repeated visitor code across secondary-index components.
