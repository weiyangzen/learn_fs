# sources/storage-engines/rocksdb/db/wide/wide_columns_helper.h

Purpose: This header declares formatting and lookup helpers for sorted RocksDB wide-column vectors. It is a small utility layer over `WideColumns` used by serialization, write-batch, and merge code.

Important APIs/types/functions: Public static APIs include `DumpWideColumns`, `DumpSliceAsWideColumns`, `HasDefaultColumn`, `HasDefaultColumnOnly`, `GetDefaultColumn`, `SortColumns`, and templated `Find`. `kDefaultWideColumnName` is the expected empty-name first column. `Find` accepts iterator ranges and a `Slice` column name.

Control flow: Default-column helpers check that the vector is non-empty and that the front column has the empty default name; `GetDefaultColumn` asserts that precondition. `SortColumns` orders columns lexicographically by name. `Find` asserts the range is already sorted, uses `std::lower_bound` by column name, and returns `end` when the exact name is absent.

State and persistence behavior: The header mutates only vectors passed to `SortColumns`. It does not own backing storage; all `WideColumn` slices continue to depend on the original string/pinned buffers.

Dependencies and integration points: It includes `<algorithm>`, `<cassert>`, `<ostream>`, `rocksdb/rocksdb_namespace.h`, and `rocksdb/wide_columns.h`. It integrates with `WideColumnSerialization` validation, merge logic that distinguishes plain default-only entities from true wide entities, and test dump rendering.

Risks: `Find` relies on debug-only sorted assertions; release builds can silently produce wrong results on unsorted inputs. `GetDefaultColumn` is assertion-only guarded, so callers must prove default-column presence. Sorting columns with slices whose backing storage is unstable can still leave dangling references.

Test signals: Serialization tests exercise `Find`, default-column paths, and sorted-column invariants. Helper tests cover dump behavior, while merge/write-batch code indirectly covers `HasDefaultColumnOnly`.
