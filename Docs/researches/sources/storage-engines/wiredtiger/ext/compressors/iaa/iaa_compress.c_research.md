
## sources/storage-engines/wiredtiger/ext/compressors/iaa/iaa_compress.c

Purpose: implements the C `WT_COMPRESSOR` adapter named `iaa`, bridging WiredTiger's compressor callbacks to the C-compatible IAA codec functions in `iaaInterface-c.h`.

Important APIs/types/functions: `iaa_COMPRESSOR` embeds `WT_COMPRESSOR` first and stores `WT_EXTENSION_API`. `iaa_compress` calls `doCompressData`, sets `compression_failed` and `result_lenp` on nonzero output, and reports `WT_ERROR` through `iaa_error` otherwise. `iaa_decompress` calls `doDecompressData` and treats nonzero result length as success. `iaa_pre_size` delegates to `getMaxCompressedDataSize`; `iaa_add_compressor` registers callbacks with `connection->add_compressor`; `iaa_extension_init` and conditionally exported `wiredtiger_extension_init` handle builtin vs module integration.

Control flow and state: initialization allocates one compressor object per connection and frees it on `terminate`. Data persistence is the QPL gzip-mode deflate stream produced by the codec; this file stores no extra prefix. Risks: all lengths are cast to `uint32_t`, so the implementation assumes WiredTiger never asks this extension to process buffers above 4 GiB. Success is inferred from result length, which makes zero-length compression/decompression ambiguous. Test signals should include round trips, incompressible data, destination-too-small behavior, corrupt input, empty input, builtin symbol collision checks, and software fallback on hosts without IAA hardware.
