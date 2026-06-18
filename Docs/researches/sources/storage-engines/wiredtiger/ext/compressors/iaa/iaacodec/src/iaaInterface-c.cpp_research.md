
## sources/storage-engines/wiredtiger/ext/compressors/iaa/iaacodec/src/iaaInterface-c.cpp

Purpose: implements the C ABI declared by `iaaInterface-c.h` by wrapping a `thread_local DB::IAA::CompressionCodecDeflate`.

Important APIs/functions: `getMaxCompressedDataSize` uses a default-constructed thread-local codec. `doCompressData` and `doDecompressData` use thread-local codecs constructed with the first `WT_COMPRESSOR` and `WT_SESSION` seen by that thread, then delegate to the aggregate codec.

Control flow and state: codec state is per thread and lives until thread exit. This caches QPL software job state per thread and shares hardware jobs globally through the pool. Integration is the narrow bridge from `iaa_compress.c`. Risks: the first compressor/session pointers captured for a thread are used for later calls on that thread, which mainly affects logging and initialization context; thread-local lifetime can outlive WiredTiger connection teardown if host thread reuse is unusual. Tests should include repeated calls across multiple sessions on the same thread, multiple threads, teardown/reload, and fallback after hardware acquisition failure.
