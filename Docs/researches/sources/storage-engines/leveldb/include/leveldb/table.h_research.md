# sources/storage-engines/leveldb/include/leveldb/table.h

Purpose: declares the immutable sorted-table reader API for SSTable files.

Important APIs and types: `Table::Open`, destructor, `NewIterator`, `ApproximateOffsetOf`, private friend `TableCache`, `BlockReader`, `InternalGet`, `ReadMeta`, and `ReadFilter`.

Control flow: `Open` reads table footer/metadata and returns a table object tied to a live `RandomAccessFile`. `NewIterator` scans table entries. `InternalGet` seeks and optionally uses filter metadata to avoid block reads. `ApproximateOffsetOf` maps a key to an estimated file byte offset.

State and persistence behavior: table files are immutable persistent storage. `Table` owns parsed metadata but not the file object, which must outlive it.

Dependencies and integration: used by `TableCache`, version reads, compactions, repair, and approximate-size APIs. Depends on iterator and options/read options.

Risks and edge cases: file-size mismatch or corrupted metadata makes `Open` fail. The file lifetime contract is easy to violate outside `TableCache`.

Test signals: table behavior is covered elsewhere; this subset exercises it through table cache, repair, recovery, and DB tests.
