# sources/sync-backup/borg/src/borg/testsuite/compress_test.py

Purpose: exercises Borg's compression facade and `CompressionSpec` parser across `none`, `lz4`, `zlib`, legacy zlib, `lzma`, `zstd`, `auto`, and size-obfuscating wrappers.

Important APIs and control flow: tests call `get_compressor`, `Compressor.compress`, `Compressor.decompress`, and `CompressionSpec(...).compressor`. Parametrized cases verify compressor class lookup, metadata fields (`ctype`, `clevel`, `csize`, `size`, `psize`), autodetection through the generic `Compressor`, legacy zlib wire compatibility, invalid compressed data handling, default and explicit level parsing, and `ArgumentTypeError` on malformed specs. Obfuscation tests cover reciprocal factor specs, additive padding specs, padme sizing (`obfuscate,250`), and object-type filtering via `ROBJ_FILE_STREAM` versus `ROBJ_ARCHIVE_META`.

State and persistence: no persistent repository state is written. Tests allocate temporary in-memory data and one 50 MiB incompressible blob to stress LZ4 buffer sizing. Randomized obfuscation assertions depend on repeated compression producing multiple output lengths.

Dependencies and integration points: depends on `borg.compress`, `borg.helpers.CompressionSpec`, Borg object-type constants, Python `zlib`, and pytest parametrization/monkeypatching. It is a contract test for archive chunk metadata consumed by repository object storage and legacy upgrade code.

Risks: output-size tests use broad statistical/range assertions and can become flaky if padding algorithms or compression ratios change. The large LZ4 test has memory cost. Legacy zlib compatibility is intentionally strict because Borg 1.x data lacks the newer extra header.

Test signals: successful round trips, exact zlib byte equality, expected metadata, parser errors, and object-type-specific no-padding for archive metadata signal compression compatibility.
