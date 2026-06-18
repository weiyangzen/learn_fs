# sources/security-integrity/encfs/src/encfsr.rs

Purpose: implements the `encfsr` reverse-mode CLI, mounting a plaintext source directory as a virtual encrypted EncFS view. It is intended for deterministic encrypted backup/export workflows using V7 configs.

Important APIs and types: `Args` defines positional `config`, `source`, and `mount_point` plus `--stdinpass`, `--extpass`, `--foreground`, and trailing FUSE options. `main` is the only runtime function beyond translated help helpers. It validates inputs, loads config, derives a cipher, builds `reverse_fs::ReverseFs`, and mounts it through `fuse_mt`.

Control flow: startup hardens the process, initializes locale and logging, validates that the source exists and is a directory, validates that the config exists and is a regular file, then loads `EncfsConfig`. It rejects non-V7 configs because reverse mode exposes the config as `.encfs7` inside the virtual filesystem. Password acquisition mirrors the main mount binary: external shell command with `RootDir`, stdin, or interactive prompt. After `config.get_cipher`, the password is zeroized. It rejects `unique_iv = true` because reverse mode requires deterministic, headerless encrypted output. It then reads config bytes and metadata, constructs `ReverseFs`, prepends read-only and default-permissions FUSE options, appends user trailing options, and mounts.

State and persistence behavior: `encfsr` does not mutate the source directory or config file during normal startup. It reads plaintext source data on demand through `ReverseFs` and presents encrypted names/content virtually. The mounted FUSE layer is forced read-only at kernel option level. Config bytes and metadata are retained in memory so the reverse filesystem can expose the config file.

Dependencies and integration points: depends on Clap, `rust_i18n`, `env_logger`, `rpassword`, `zeroize`, shell `sh -c` for extpass, `config`, `security::harden_process`, `reverse_fs::ReverseFs`, and `fuse_mt`. It shares password/cipher derivation with the normal mount path but delegates all reverse filesystem semantics to `reverse_fs`.

Risks: all hard failures print an error and call `std::process::exit(1)` rather than returning structured errors, which is fine for a CLI but harder to unit-test. `--extpass` executes through the shell and is trusted. Reverse mode rejects `unique_iv = true`, so many normal EncFS configs cannot be mounted until created or migrated with compatible settings. User-supplied trailing FUSE options are appended after `ro` and `default_permissions`; depending on FUSE parsing, conflicting options may still affect behavior.

Test signals: no embedded tests in this file. Coverage is expected from `reverse_fs` tests, config loading tests, and manual CLI/FUSE integration tests. Startup validation paths, FUSE option composition, and V7/unique-IV rejection are not directly unit-tested here.
