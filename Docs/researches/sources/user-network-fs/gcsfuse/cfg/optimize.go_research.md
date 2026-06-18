## sources/user-network-fs/gcsfuse/cfg/optimize.go

Purpose: Implements generic auto-configuration support used by generated `Config.ApplyOptimizations`.

Important APIs/types/functions: constants `maxRetries`, `httpTimeout`, and `machineTypeFlg`; `OptimizationResult` records final value, reason, and non-serialized `Optimized`; package variable `metadataEndpoints`; helpers `getMetadata`, `getMachineType`, `isFlagPresent`, `getOptimizedValue`, and `CreateHierarchicalOptimizedFlags`.

Control flow: `getMachineType` first honors Viper `machine-type`, then tries metadata endpoints with short-timeout HTTP GETs using `Metadata-Flavor: Google`, returning the last path segment. `getOptimizedValue` applies precedence profile, machine-type group, bucket type, then current value. `CreateHierarchicalOptimizedFlags` splits dot-separated keys into nested maps and rejects terminal/path conflicts.

State and persistence: `metadataEndpoints` is mutable package state, primarily for tests. Optimization results are in-memory only and explicitly hide `Optimized` from YAML/JSON.

Dependencies and integration points: imports HTTP, Viper, slices, strings, time, and `cfg/shared` rule types. Consumed by generated config optimization and logs/status code that wants nested optimized flag structures.

Risks: metadata lookup silently falls back to no machine optimization when unavailable in `ApplyOptimizations`. Retry loop has no backoff. Mutable `metadataEndpoints` can create test races if tests become parallel. The comment says profile takes precedence, but code will still apply machine optimization when a non-matching profile string is set.

Test signals: `optimize_test.go` covers metadata failure/success/retry, user-provided machine type precedence, disabled autoconfig, matching/nonmatching machine types, user-set flag preservation, successful high-performance optimizations, and hierarchical map conflict detection.
