## sources/security-integrity/cryfs/crates/cli-utils/src/env.rs

Purpose: reads and documents CryFS environment variables that affect frontend interactivity, update checks, and local integrity-state storage.

Important APIs and types: `EnvVarDoc` documents variables. `ENV_VARS_DOCUMENTATION` lists `CRYFS_FRONTEND=noninteractive`, optional `CRYFS_NO_UPDATE_CHECK=true`, and `CRYFS_LOCAL_STATE_DIR=[path]`. `Environment` stores `is_noninteractive`, optional `no_update_check`, and `local_state_dir`. `Environment::read_env` is crate-visible.

Control flow and state: `is_noninteractive` returns true only for exact `noninteractive`. `no_update_check` returns true only for exact `true`. `local_state_dir` canonicalizes an explicitly set path and errors if inaccessible; otherwise it defaults to `dirs::data_local_dir()/cryfs`.

Dependencies and integration: maps local-state errors to `CliErrorKind::InaccessibleLocalStateDir`. `Application::_run` reads this environment before parsing args. Version output uses noninteractive/no-update flags; blockstore setup uses local state later.

Risks and test signals: tests cover unset, exact, empty, other, nonunicode, existing, nonexisting, absolute, and relative local-state cases. The documentation string embeds a hard-coded example default path, which can drift from actual platform-specific defaults.
