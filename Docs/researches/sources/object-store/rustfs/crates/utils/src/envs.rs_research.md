# sources/object-store/rustfs/crates/utils/src/envs.rs

Purpose: Central environment parsing and compatibility helpers for RustFS.

Important APIs/state: Numeric getters for signed/unsigned/floating types, optional variants, `get_env_str`, `get_env_bool`, alias-aware variants, `ExternalEnvCompatReport`, `build_external_env_compat_report`, and `apply_external_env_compat`. Warning de-duplication uses `OnceLock<Mutex<HashSet<String>>>`.

Control flow: Canonical env key takes precedence. Deprecated aliases are checked next with one-time warnings. For `RUSTFS_*` keys, selected external-prefix variables are accepted when the suffix is in an allowlist or dynamic notification/audit prefix. Parsing failures generally fall back to defaults or `None`; bool parsing accepts many truthy/falsy tokens. Compatibility report maps source-prefixed variables to missing `RUSTFS_*` names and records conflicts when both exist with different values. `apply_external_env_compat` copies mappable values into the current process and is marked unsafe because env mutation should occur before threads.

Dependencies and integration: Used by trusted-proxies config loader for booleans/strings/numbers and by broader RustFS configuration bootstrap.

Risks and tests: Generic numeric getters do not log invalid values except specialized alias-aware paths, which can hide bad config. Global warning state makes warning assertions order-dependent. Tests cover source-prefix mapping, conflicts, dynamic suffixes, ignored keys, alias precedence, invalid i32 alias fallback, and applying compatibility mappings.
