# sources/object-store/garage/src/garage/secrets.rs

Purpose: This file centralizes secret injection for CLI/server operation. It lets RPC, admin API, and metrics tokens be supplied either directly or through files from config, CLI flags, or environment variables, while enforcing mutual exclusion and optional Unix permission checks.

Important APIs and types: `Secrets` is a `StructOpt`-derived CLI/env struct for `rpc_secret`, `rpc_secret_file`, `admin_token`, `admin_token_file`, `metrics_token`, `metrics_token_file`, and `allow_world_readable_secrets`. `fill_secrets` applies all secret overrides to a `Config`. `fill_secret` resolves one secret value. `read_secret_file` performs permission checks and trims trailing whitespace.

Control flow: `fill_secrets` chooses the effective `allow_world_readable` policy from CLI/env override or config default, then calls `fill_secret` for each supported secret. `fill_secret` first rejects simultaneous direct and file values from CLI/env, then overrides config if a CLI/env value exists, otherwise reads the config file path if present. If both config direct value and config file path are present it errors. Secret files are read as text and `trim_end` is applied.

State and persistence behavior: No persistent writes occur. The function mutates the in-memory `Config` so downstream code sees resolved secret strings rather than file paths. On Unix, the permission check refuses any group/world permission bits unless explicitly allowed.

Dependencies and integration points: It depends on `garage_util::config::Config`, `garage_util::error::Error`, `structopt`, and Unix `MetadataExt`. `main.rs` uses `fill_secret` for remote CLI RPC secrets, while `server.rs` uses `fill_secrets` before constructing `Garage`.

Risks: Direct CLI/env secrets override config values and may hide deployment mistakes. The world-readable check is Unix-only; behavior differs on non-Unix. `trim_end` is convenient for newline-terminated secret files but would also remove intended trailing whitespace if a secret format allowed it. Error messages name `*_file` even when paths came from environment variables, which is accurate to the logical option but not always the source.

Test signals: Unit tests create temporary config and secret files, verify secret file reading, override precedence for direct/file CLI values, Unix permission failures and overrides, and rejection when both `rpc_secret` and `rpc_secret_file` are configured.
