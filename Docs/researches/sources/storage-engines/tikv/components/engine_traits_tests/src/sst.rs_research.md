# sources/storage-engines/tikv/components/engine_traits_tests/src/sst.rs

Purpose: Tests generic SST writer, reader, iterator, and metadata contracts.

Important APIs and control flow: Tests build SST writers through `SstWriterBuilder`, expect finishing an empty writer to return an engine error, write ordered keys and read them with `SstReader` iterators forward/reverse, verify delete-only SSTs produce invalid data iterators, reject duplicate or reverse-order keys, and validate external SST metadata such as file path, smallest/largest key, entry count, and file size. Sequence-number metadata has an ignored placeholder test.

State, persistence, and dependencies: Each test creates a temporary SST file and reads filesystem metadata. Reader/writer behavior may involve backend table format and optional encryption manager support, though these tests pass `None`.

Integration points, risks, and test signals: Covers import/backup-ready external SST semantics. Risks include incorrect ordered-key enforcement, tombstone-only iterator visibility, metadata mismatch with actual file size, delete entry counting, and untested sequence-number behavior.
