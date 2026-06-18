
## sources/storage-engines/wiredtiger/ext/compressors/nop/nop_compress.c

Purpose: sample `WT_COMPRESSOR` implementation that copies data unchanged while exercising the compressor extension API.

Important APIs/types/functions: `NOP_COMPRESSOR` embeds `WT_COMPRESSOR`, stores `WT_EXTENSION_API`, and counts calls. `nop_compress` copies `src` to `dst` when capacity permits and sets `compression_failed` on short destination. `nop_decompress` copies `dst_len` bytes from source to destination and reports `dst_len`. `nop_pre_size` returns `src_len`. `wiredtiger_extension_init` allocates the compressor and registers it as `nop`.

State and persistence: call count lives in the compressor object only; persisted bytes are identical to input. Risks: `nop_decompress` trusts WiredTiger's expected output length and does not independently verify `src_len >= dst_len`; this is acceptable for an example but not defensive against corrupt inputs. Tests should cover load/unload, destination-too-small compression, pass-through round trips, and terminate freeing the heap object.
