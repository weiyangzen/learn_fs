# sources/test-tools/syzkaller/pkg/cover/report_test.go

Purpose: Linux-only integration tests for report generation across target OS/architecture definitions and multiple binary/debug/coverage configurations.

Important APIs/types/functions: `TestReportGenerator`, `testReportGenerator`, `kcovCode`, `buildTestBinary`, `generateReport`, `checkCSVReport`, `checkJSONLReport`, `TestCoverByFilePrefixes`, and fixtures `sampleJSONLlProgs` plus `makeFileStat`.

Control flow: tests iterate supported targets for the host build OS, compile small C binaries with optional sanitizer coverage, debug info, PIE, and relocation flags, discover modules, build a `ReportGenerator`, optionally run the binary to collect a callback PC, and exercise HTML, subsystem, file, function CSV, coverage JSONL, and per-program JSONL outputs. Expected error regexes cover no coverage callbacks, missing debug info, no PCs, bad PCs, and callback mismatches.

State and persistence: writes temporary source/object/binary files in `t.TempDir`; no repo files modified.

Dependencies and integration: depends on syzkaller target metadata, cross-compilers, `osutil`, `symbolizer`, and backend module discovery. It exercises `backend`, `report.go`, and `html.go` together.

Risks: many subtests skip depending on host, compiler availability, broken compiler metadata, target support, and sanitizer/runtime behavior. PC values are normalized in JSON comparison because exact addresses vary.

Test signals: strongest end-to-end signal for coverage report correctness, including generated JSON schemas and subsystem aggregation exclusions.
