## sources/object-store/rustfs/crates/tls-runtime/src/config.rs

Purpose: defines shared TLS reload options and enum knobs for the foundation runtime and target adapters.

Important APIs/types/functions: `ReloadDetectMode::{Poll, Watch, Hybrid}` models detection strategy; watch and hybrid are marked TODO for fs-watch implementation. `ReloadApplyHint::{Lazy, SoftReconnect}` tells consumers how aggressively to apply new material. `TlsReloadOptions` contains `enabled`, `detect_mode`, `interval`, `debounce`, `min_stable_age`, and `apply_hint`. `Default` enables poll reload every 15 seconds, 2 second debounce, 1 second min stable age, and lazy apply.

Control flow and state: no mutable state. Options are copied/cloned into coordinators and adapters.

Dependencies and integration points: imported directly by `rustfs-tls-runtime` and re-exported/aliased by target TLS config. Runtime coordinators currently implement polling; watch/hybrid naming is present before full watch behavior.

Risks: fields `debounce` and `min_stable_age` are not uniformly enforced across all reload paths; target coordinator uses debounce and shared foundation coordinator currently uses interval only. Watch mode skips target poll loop even though fs-watch is TODO, so consumers choosing Watch may get no automatic reload.

Test signals: no local tests; defaults are used in coordinator/server tests.
