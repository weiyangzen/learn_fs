# sources/sync-backup/kopia/repo/compression/compression_ids.go

Purpose: reserves stable four-byte header IDs for every supported or historically supported content compressor.

Important APIs/types/functions: `HeaderID` is a `uint32`; constants cover gzip, zstd, s2, pgzip, removed LZ4, and deflate variants.

Control flow: compressor implementations register themselves with one of these IDs and write the big-endian ID as a compression header. `DecompressByHeader` uses the ID to dispatch.

State and persistence behavior: these IDs are persisted inside compressed repository content, so values are wire/storage format and must not be reused incompatibly. `headerLZ4Removed` remains reserved for old repositories even though the implementation is unsupported.

Dependencies/integration: used by every compressor implementation and content read/decompression paths.

Risks and edge cases: changing IDs or reusing removed IDs would make existing repositories unreadable or misdecoded.

Test signals: compressor tests iterate registered IDs, round-trip data, and verify wrong compressors reject mismatched headers.
