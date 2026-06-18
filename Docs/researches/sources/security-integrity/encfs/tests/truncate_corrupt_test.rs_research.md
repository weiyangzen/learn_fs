# sources/security-integrity/encfs/tests/truncate_corrupt_test.rs

Purpose: regression tests for encrypted file truncation and extension around partial blocks, MAC tags, and sparse/hole behavior.

Important APIs/types/functions: uses deterministic `EncFs` setup, `create`, `write`, `truncate`, `release`, `FileExt::read_at`, `SslCipher::decrypt_header`, and `FileDecoder`.

Control flow: `test_truncate_corrupts_partial_block` writes 1074 bytes, releases, truncates to 500 bytes, decrypts the physical file, and asserts the remaining plaintext equals the original prefix. It targets corruption caused by decrypting a formerly full CBC block as a partial block. `test_truncate_extend_then_append_preserves_block0_tag` enables `allow_holes`, writes a partial block payload, extends to two data blocks, appends after the hole, then decrypts and asserts original prefix, zero-filled hole, and appended payload.

State and persistence: writes temporary backing files and removes temp roots.

Dependencies and integration points: exercises block encoder/decoder, file headers, logical/physical size translation, MAC tag preservation, and hole zero-fill semantics.

Risks: physical file discovery assumes a single backing entry. Tests use fixed 1024 block size and 8 MAC bytes via defaults.

Test signals: strong data-integrity guard for truncation bugs that can silently corrupt encrypted contents.
