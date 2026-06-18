## sources/user-network-fs/gcsfuse/cfg/config_test.go

Purpose: Generated unit tests for `Config.ApplyOptimizations` across every generated optimization rule.

Important APIs/types/functions: single `TestApplyOptimizations` with subtests for `file-system.congestion-threshold`, `file-system.enable-kernel-reader`, `file-cache.cache-file-for-range-read`, `write.finalize-file-for-rapid`, `implicit-dirs`, `file-system.kernel-list-cache-ttl-secs`, `file-system.max-background`, `file-system.max-read-ahead-kb`, `metadata-cache.negative-ttl-secs`, `metadata-cache.ttl-secs`, `file-system.rename-dir-limit`, `metadata-cache.stat-cache-max-size-mb`, and `write.global-max-blocks`.

Control flow: for each flag, table cases set up a `Config`, optional Viper user-set flags, optional `OptimizationInput`, expected optimized/no-op status, and expected final value. The test copies config, seeds field defaults/user values, calls `ApplyOptimizations`, asserts presence or absence in the returned map, and checks the mutated field.

State and persistence: no persistent state; Viper/config instances are local per case.

Dependencies and integration points: uses `viper` and `testify/assert`; validates generated rules in `config.go` and generic logic in `optimize.go`.

Risks: because tests are generated with the code, template bugs can be replicated in both implementation and expectations. Some cases rely on `machine-type` Viper values instead of metadata server, avoiding network nondeterminism but not testing lookup here.

Test signals: strong regression signal for optimization precedence and user override preservation for each generated flag.
