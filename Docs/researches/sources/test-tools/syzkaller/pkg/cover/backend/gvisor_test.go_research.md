# sources/test-tools/syzkaller/pkg/cover/backend/gvisor_test.go

Purpose: validates parsing of gVisor `symbolize -all` output and the path regex used by the gVisor coverage backend.

Important APIs/types/functions: `TestGvisorParseLine` reads fixture files from `test_data`; `TestGvisorLineRe` checks `gvisorLineRe` path capture.

Control flow: fixture scanning passes a shared scanner through `gvisorParseLine`, which consumes PC and line-info records. Regex tests match sample source paths and compare capture group 2 to the expected `pkg/...` path.

State and persistence: read-only fixture files; no writes.

Dependencies and integration: depends on checked-in `test_data/symbolize_all_gvisor_*` files and same-package backend internals.

Risks: `lineNum` is incremented but not used for diagnostics. Fixture coverage is broad for historical gVisor outputs but does not test process execution or filesystem fallback behavior.

Test signals: parsing failures catch format drift in gVisor symbolize output before report generation loses all gVisor frames.
