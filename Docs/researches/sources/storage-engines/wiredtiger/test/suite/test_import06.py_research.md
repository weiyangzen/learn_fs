# sources/storage-engines/wiredtiger/test/suite/test_import06.py

Purpose: tests `repair=true` file import without supplied file metadata across allocation sizes, compression extensions, and encryption extensions.

Important APIs and functions: scenarios combine allocation sizes 512-4096, compressors (`none`, `nop`, `lz4`, `snappy`, `zlib`, `zstd`), and encryptors (`none`, `nop`, `rotn`, `sodium`). `conn_extensions` loads compressor/encryptor extensions with `skip_if_missing`; `conn_config` configures encryption including the sodium test key.

Control flow: the test creates an encrypted/compressed file, writes/checkpoints two batches, exports metadata only for later comparison, closes, opens `IMPORT_DB` with compatible encryption config, populates unrelated files, advances oldest timestamp, copies the data file, imports with `import=(enabled,repair=true)`, verifies, checks imported rows, compares reconstructed metadata with original metadata, appends remaining rows, and checkpoints.

State and persistence behavior: repair import reconstructs metadata from the file itself, so allocation size, compression, and encryption metadata must be discoverable and compatible with the destination connection.

Dependencies and integration points: integrates extension loading, encryption/compression configuration, repair import, metadata comparison, and binary key/value data.

Risks and edge cases: extension availability controls scenario skips. Encryption mismatches would surface at import/open time. The `nop` encryptor scenario maps to `encryptor='none'` in this file, which may reflect test naming rather than a true nop encryptor.

Test signals: import succeeds, verification passes, metadata comparison succeeds, and subsequent writes/readbacks work.
