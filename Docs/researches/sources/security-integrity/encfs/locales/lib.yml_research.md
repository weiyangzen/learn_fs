## sources/security-integrity/encfs/locales/lib.yml

Purpose: Small library-level i18n catalog for errors emitted from non-CLI code paths.

Important APIs and keys: `_version: 2`, `lib.error_end_of_buffer`, `lib.error_version3_not_supported`, and `lib.error_unsupported_cipher` with `%{name}` and `%{key_size}` placeholders. Control flow is through `t!()` calls in modules such as `config_binary.rs` and `config.rs`.

State and persistence: Static localized error text only. Dependencies are `rust-i18n` and exact placeholder compatibility. Integration: these messages surface when parsing legacy binary configs, rejecting very old config versions, or constructing unsupported ciphers. Risks are limited catalog coverage: many library errors remain hardcoded English, so localization is partial and callers must handle mixed-language diagnostics.
