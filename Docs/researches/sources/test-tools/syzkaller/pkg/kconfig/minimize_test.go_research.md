## sources/test-tools/syzkaller/pkg/kconfig/minimize_test.go

Purpose: validates Kconfig minimization logic.

Important APIs/types/functions: `TestMinimize`.

Control flow: constructs base/full configs and Kconfig relationships, runs `Minimize` with a predicate, and asserts minimized output/suspects.

State and persistence: uses debug tracer outputs in test context.

Dependencies and integration: covers interactions between config parsing, dependency closure, and generic minimizer.

Risks: test scenarios are synthetic and may not cover all kernel dependency quirks.

Test signals: direct unit signal for minimizing leaf configs plus dependencies.
