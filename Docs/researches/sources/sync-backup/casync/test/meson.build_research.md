# sources/sync-backup/casync/test/meson.build

Purpose: registers casync tests with Meson.

Important APIs/types/functions: defines test executables and shell-script tests, linking them against `libshared` and using configured `.sh.in` scripts.

Control flow/state: build-time orchestration only. The file determines which C tests and integration scripts run under `meson test`.

Dependencies/integration: depends on source targets from `src/meson.build`, optional feature flags, and generated config substitutions.

Risks/test signals: if a test is omitted here, regressions in that area may be invisible to CI. Keeping the list synchronized with test files is the primary maintenance concern.

Source research group: `subset-b-009122`.
