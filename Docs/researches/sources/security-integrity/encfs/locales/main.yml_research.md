## sources/security-integrity/encfs/locales/main.yml

Purpose: Runtime i18n catalog for the primary `encfs` binary and `encfsr` reverse-mode executable. It covers mount messages, config discovery, password prompting, daemonization, volume-key decryption, and reverse-mode validation errors.

Important APIs and keys: `main.mounting`, `main.using_legacy_config`, `main.no_config_file_found`, `main.failed_to_read_password`, `main.successfully_decrypted`, `main.daemonized_successfully`, `main.failed_to_decrypt_key`, `main.extpass_program_failed`, and `encfsr.*` validation messages. Control flow is data-driven via `rust-i18n` lookups from main/reverse binary code.

State and persistence: Static localization data. Dependencies are placeholder alignment with call sites (`%{root}`, `%{mount_point}`, `%{error}`, `%{source}`, `%{path}`). Integration is important for security UX because password and decrypt failure messages are user-facing. Risks include incomplete implementation notes (`encfsr.mount_not_implemented`) becoming stale if reverse mounting is implemented without updating locale text.
