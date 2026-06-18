## sources/security-integrity/encfs/src/config_binary.rs

Purpose: Parser for legacy EncFS binary configuration variables used by V4/V5 configs. It provides a byte-buffer cursor abstraction and a top-level key/value reader.

Important APIs and types: `ConfigVar`, `ConfigVar::new`, `at`, `read_int`, `read_int_default`, `read_bool`, `read_bytes`, `read_string`, `read_u8_vector`, `ConfigReader`, `ConfigReader::new`, `ConfigReader::get`. Control flow decodes variable-length integers with high-bit continuation, then length-prefixed byte/string values; `ConfigReader` reads an entry count and then repeated key/value blobs into a `HashMap`.

State and persistence: In-memory buffers and cursor offsets; persistent source is legacy `.encfs4/.encfs5` bytes. Dependencies are anyhow, rust-i18n for end-of-buffer error, and standard collections. Integration is used by `config.rs` `load_v4`/`load_v5` and `Interface::from_config_var`. Risks include accepting malformed VLQ sequences that end at buffer boundary without explicit continuation error, and UTF-8 validation that may be stricter than historical C++ behavior. Unit tests cover VLQ, string, and reader basics.
