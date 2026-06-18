
## sources/storage-engines/wiredtiger/ext/compressors/nop/CMakeLists.txt

Purpose: builds the sample no-op compressor as `wiredtiger_nop_compress` from `nop_compress.c`.

Integration: this is always a shared library target rather than a builtin-configurable target. It includes WiredTiger source/generated/config headers and applies C diagnostic flags. It does not link a third-party compression library.

State: no build-time persistence. Risks are mostly sample-extension drift from the current `WT_COMPRESSOR` ABI and absence of install logic in this file. Test signals are module load and a pass-through compression/decompression round trip.
