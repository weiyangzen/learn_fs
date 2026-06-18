## sources/security-integrity/encfs/locales/ctl.yml

Purpose: i18n catalog for `encfsctl` administrative messages in English, French, and German. It covers config info display, password changes, Argon2 upgrade/calibration, cruft scanning, encoding/decoding, export, `cat`/`ls`, and new V7 config creation errors/prompts.

Important APIs and keys: `_version: 2` and many `ctl.*` keys such as `ctl.version7_config`, `ctl.v7_format_info`, `ctl.block_mode_aes_gcm_siv`, `ctl.kdf_algorithm_argon2id`, password prompts, file decode/export warnings, config-load/password errors, and `ctl.new_*`. Control flow is data-driven through `rust-i18n` `t!()` lookups from Rust CLI code.

State and persistence: No runtime state; persistent source of localized UI strings. Dependencies are YAML syntax and placeholder names matching call sites (`%{path}`, `%{error}`, etc.). Integration affects user-facing diagnostics and command help consistency. Risks include placeholder mismatches, untranslated semantic drift, and security-sensitive wording around invalid password/tampered config that must remain clear across locales.
