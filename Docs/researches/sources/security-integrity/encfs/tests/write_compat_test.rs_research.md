# sources/security-integrity/encfs/tests/write_compat_test.rs

Purpose: verifies write compatibility across legacy-like and paranoia-like configurations, plus `fstat` and `statfs` behavior.

Important APIs/types/functions: `setup_test_fs` parameterizes AES major version, key size, block size, block MAC bytes, chained name IV, and external IV chaining. Tests use `create`, `write`, `getattr`, `unlink`, `release`, `statfs`, and manual `FileDecoder` verification.

Control flow: `test_write_legacy_v2` writes and decrypts data with major 2, AES-192, no chained IV, no MAC. `test_write_paranoia` writes under AES-256, 8-byte MAC, chained and external IV, recovers filename IV from encrypted backing name, then decrypts header/content. `test_fstat_support` validates size through handle and path, then unlinks while open and confirms handle-based getattr still works while path getattr fails. `test_statfs_support` checks root statfs returns plausible values.

State and persistence: creates temp roots and encrypted backing files, then removes them.

Dependencies and integration points: covers write path, header IV handling, name IV derivation, handle table semantics, unlink-open behavior, and statvfs translation.

Risks: uses synthetic configs rather than historical fixtures for legacy write. Directory entry discovery assumes a small controlled temp root.

Test signals: important compatibility signal for writes across config modes and for POSIX-style metadata behavior.
