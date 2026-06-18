# sources/test-tools/syzkaller/syz-ci/config_test.go

Purpose: unit tests for syz-ci config loading and baseline config inference.

Important APIs/types/functions: `TestLoadConfig`, `TestBaselineCanInference`, and `TestBaselineCannotInference`.

Control flow: loads `testdata/example.cfg`, then creates temporary `kernel.config`/`kernel-base.config` files to check inferred baseline path behavior.

State and persistence: temporary files only.

Dependencies and integration points: exercises `loadConfig` and `inferBaselineConfig` from `syz-ci.go`.

Risks: example config covers basic schema but not most validation paths.

Test signals: config parser and baseline inference regressions.
