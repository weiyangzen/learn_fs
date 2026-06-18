# sources/storage-engines/rocksdb/util/file_checksum_helper.h

Purpose: declares default CRC32C file checksum generator and in-memory file checksum list implementation.

Important types/APIs: `FileChecksumGenCrc32c` implements `FileChecksumGenerator` with `Update()`, `Finalize()`, `GetChecksum()`, and `Name()`. `FileChecksumGenCrc32cFactory` creates the generator when no checksum name or `"FileChecksumCrc32c"` is requested. `FileChecksumListImpl` implements CRUD/list APIs over file-number checksums.

Control flow: `Update()` extends running CRC32C. `Finalize()` stores the checksum as big-endian raw bytes via `PutFixed32(EndianSwapValue(checksum_))`. `GetChecksum()` asserts finalization occurred.

State and persistence: generator stores `uint32_t checksum_` and finalized string. The byte order and algorithm name are persisted/externally visible through file checksum metadata. List implementation stores map entries in memory.

Dependencies and integration: depends on public `rocksdb/file_checksum.h`, coding, CRC32C, and math endian helpers. Used by DB/file writing options as the default SST file checksum method.

Risks: calling `GetChecksum()` before `Finalize()` or `Finalize()` twice triggers assertions. Changing endian storage would break compatibility with existing checksum consumers. Factory matching is string-based.

Test signals: writer checksum handoff in `file_reader_writer_test.cc`; direct generator tests are not in this subset.
