# sources/sync-backup/kopia/repo/compression/compressor_lz4.go

Purpose: preserves the historical LZ4 compressor name/header while making it explicitly unsupported in current Kopia versions.

Important APIs/types/functions: init calls `registerUnsupportedCompressor("lz4", lz4Compressor{})`; `errLZ4NotSupported` explains that v0.22.3 or older is needed for legacy repositories; `lz4Compressor` implements `HeaderID`, `Compress`, and `Decompress`.

Control flow: registration adds the name/header to global maps, marks it deprecated and unsupported, and both compression/decompression calls return the fixed unsupported error.

State and persistence behavior: `headerLZ4Removed` remains reserved for existing content and must not be reused. No new LZ4 content can be created by this implementation.

Dependencies/integration: `IsSupported("lz4")` returns false even though `ByName`/`ByHeaderID` can recognize it.

Risks and edge cases: repositories that still contain LZ4-compressed data cannot be read by this version. Keeping the ID registered avoids silent reinterpretation by a future compressor.

Test signals: compressor tests skip unsupported IDs; direct coverage should assert `IsSupported("lz4") == false` and the explanatory error.
