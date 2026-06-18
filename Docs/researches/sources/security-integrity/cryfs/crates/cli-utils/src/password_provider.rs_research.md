## sources/security-integrity/cryfs/crates/cli-utils/src/password_provider.rs

Purpose: implements interactive and noninteractive password acquisition for config loading/creation.

Important APIs and types: `InteractivePasswordProvider` and `NoninteractivePasswordProvider` implement `cryfs_config::config::PasswordProvider`. `ask_password_from_console` prompts through `rpassword::prompt_password` with styled indentation. `check_password` rejects empty passwords.

Control flow and state: interactive existing-filesystem flow loops until a nonempty password is entered. Interactive new-filesystem flow also asks for confirmation and loops on mismatch. Noninteractive flows ask once and return an error for empty input without confirmation. Passwords are plain `String`s and are not persisted by this module.

Dependencies and integration: depends on `anyhow::ensure`, `console::style`, `rpassword`, and `cryfs_config`. CLI applications choose provider based on environment/front-end mode.

Risks and test signals: a TODO notes password memory hardening is missing; strings are not mprotected or zeroized. Another TODO notes missing tests. Noninteractive mode intentionally skips confirmation, useful for automation but easier to misuse when creating a new filesystem.
