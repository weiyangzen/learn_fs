## sources/security-integrity/cryfs/crates/cli-utils/src/application.rs

Purpose: generic CLI runner for CryFS binaries. It coordinates panic handling, environment reading, argument parsing, logging initialization, version/update output, application construction, main execution, and process exit-code mapping.

Important APIs and types: `Application` trait defines `ConcreteArgs`, `NAME`, `VERSION`, `new`, `default_log_config`, `should_show_version`, `defer_logging_init`, and `main`. `run<App>() -> ExitCode` wraps `_run<App>()` and prints `CliError`s. `DEFAULT_LOG_LEVEL` is `Info`. `show_backtrace_on_panic` configures debug backtraces or release `human_panic`.

Control flow and state: `_run` sets panic behavior, reads `Environment`, builds a version-display closure, parses args, handles `--version`, normal app startup, clap exits, and non-clap parse errors. Logging is initialized unless deferred; version output occurs before `main` unless disabled by the app.

Dependencies and integration: depends on `clap`, `clap_logflag`, `cryfs_version`, `human_panic`, environment and error modules, and optional update-check HTTP client. Downstream binaries implement `Application`.

Risks and test signals: clap errors call `err.exit()`, so that branch never returns normally. Version output to stderr can happen before logging initialization. Daemon-style apps can suppress banners and defer logging, which reduces accidental TTY output but shifts responsibility to the application.
