# sources/storage-engines/leveldb/include/leveldb/slice.h

Purpose: declares `Slice`, LevelDB's lightweight non-owning byte-string view.

Important APIs and types: constructors from pointer/length, `std::string`, and C string; `data`, `size`, `empty`, `begin`, `end`, `operator[]`, `clear`, `remove_prefix`, `ToString`, `compare`, `starts_with`, equality and inequality operators.

Control flow: APIs pass keys, values, encoded metadata, and file-read results as `Slice`s to avoid copies. Parsing code mutates local slices with `remove_prefix`.

State and persistence behavior: no ownership or persistence; it may refer to persistent bytes, scratch buffers, strings, or in-memory encoded records owned elsewhere.

Dependencies and integration: used throughout public and internal APIs. Comparators and filters interpret slices as byte sequences.

Risks and edge cases: caller must ensure backing storage outlives the slice. C-string constructor uses `strlen`, so embedded NUL data requires pointer/length construction. `operator[]` and `remove_prefix` enforce bounds only through asserts.

Test signals: indirectly covered everywhere; no direct slice tests in this subset.
