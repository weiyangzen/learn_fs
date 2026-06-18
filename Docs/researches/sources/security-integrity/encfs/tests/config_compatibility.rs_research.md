# sources/security-integrity/encfs/tests/config_compatibility.rs

Purpose: broad compatibility suite for EncFS config formats and encrypted fixture readability across V5 binary configs, V6 XML standard mode, and V6 XML paranoia mode.

Important APIs/types/functions: helper `load_and_verify_config` loads `EncfsConfig` and derives a cipher. `decrypt_path_result` adapts `EncFs::decrypt_path` error codes to `anyhow`. `read_and_hash_file` opens encrypted fixture files, decrypts path IV and file header, constructs `FileDecoder`, reads plaintext, and returns SHA1. Tests cover `test_v5_binary_config_format`, `test_v6_xml_config_format_standard`, `test_v6_xml_config_format_paranoia`, cipher/key-size/mode/feature/KDF/block-name checks, cross-version loading, and random-access read operations.

Control flow: each test selects fixture roots, loads config with password `test`, asserts config fields, derives `SslCipher`, constructs `EncFs`, decrypts known encrypted names, and often verifies SHA1 `4240880c2ecba8d2315bad8b27b8674cc59b268c` for `DESIGN.md`. Paranoia tests additionally assert nonzero path IV and block MAC handling.

State and persistence: reads fixture files only. No persistent writes occur.

Dependencies and integration points: depends on fixture layout under `tests/fixtures` and `tests/fixtures/encfs142`, SHA1 hashing, `FileDecoder`, and `EncFs` path decryption.

Risks: tests panic if fixtures are missing, so fixture packaging is required. Some tests duplicate setup and only verify available AES fixtures; Blowfish is acknowledged but not covered. Hash checks lock expected plaintext content.

Test signals: high-value compatibility signal for config parsing, KDF behavior, header IV derivation, block MAC stripping, chained/external IV features, and random-access file decode.
