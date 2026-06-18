# sources/security-integrity/encfs/src/main.rs

Purpose: implements the normal `encfs` mount binary. It parses mount options, finds and loads an EncFS config, obtains the password, derives the cipher, optionally daemonizes, constructs `EncFs`, and mounts it with selected FUSE options.

Important APIs and types: `Args` defines `--foreground`, `--verbose`, `-d` debug mode, `-s` single-thread mode, `--public`, `--extpass`, `--stdinpass`, `--read-only`, `--no-default-permissions`, and positional `root`/`mount_point`. `main` handles all runtime behavior. Translated help helper functions supply Clap strings.

Control flow: startup hardens the process, initializes locale, parses CLI args, configures logging, and searches the encrypted root for `.encfs7`, `.encfs6.xml`, then `.encfs5`. It loads `EncfsConfig`, acquires the password from an external shell command, stdin, or prompt, calls `config.get_cipher`, and zeroizes the password. On success it daemonizes unless foreground/debug is active, constructs `EncFs::new`, builds FUSE options for `allow_other`, `default_permissions`, and `ro`, selects the FUSE worker count, and calls `fuse_mt::mount`. On cipher failure it logs and returns the underlying error.

State and persistence behavior: `main.rs` itself does not write config or encrypted data before mounting. After mount, persistence is delegated to `EncFs`. It passes read-only FUSE option when requested but does not otherwise alter the loaded config. The password string is zeroized after cipher derivation.

Dependencies and integration points: depends on Clap, `daemonize`, `env_logger`, `log`, `rust_i18n`, `rpassword`, shell `sh -c` for extpass, `security::harden_process`, `config::EncfsConfig`, `fs::EncFs`, and `fuse_mt`. It is the top-level integration point for `fs.rs` and the config/crypto stack.

Risks: config discovery ignores `.encfs4` and `.encfs3` even though `encfsctl` can detect them, so behavior differs between mount and utility. `--extpass` uses the shell and is trusted input. Daemonization happens after password verification but before FUSE mount, so foreground diagnostics differ from daemon diagnostics. `--public` can add `allow_other`; security then depends on system FUSE policy and the selected `default_permissions` behavior. There is no support for arbitrary trailing FUSE options in this binary.

Test signals: no embedded tests in this file. Behavior is covered indirectly by tests of `config`, `SslCipher`, and `EncFs`, while full CLI option parsing, daemonization, config search precedence, and FUSE mount option composition require integration or manual tests.
