# Research: sources/test-tools/syzkaller/pkg/report/linux_test.go

Purpose: focused unit tests for Linux-specific reporter behavior that is too detailed for generic parse fixtures: ignore filtering, fault-injection extraction, backtrace symbolization, opcode parsing, and report disassembly.

Important APIs/types/functions: `TestLinuxIgnores` validates configured ignore regexps. `TestExtractFaultInjectionInfo` and `TestExtractFaultInjectionInfoDeduplicates` validate compact extraction and duplicate suppression. `TestLinuxSymbolizeLine` builds fake symbols/modules and a fake symbolizer to test `linux.symbolize`. `prepareLinuxReporter` creates an AMD64 or requested-arch reporter. `TestParseLinuxOpcodes` validates `parseOpcodes` for little-endian, big-endian, ARM Thumb, and malformed strings. `TestDisassemblyInReports` and `testDisassembly` compare `Code:` decompilation fixtures.

Control flow: tests construct minimal `mgrconfig.Config` values, parse synthetic logs, call Linux internals directly where needed, and compare exact strings or structs. Symbolization tests route selected PCs to controlled frames, including inline frames and errors. Disassembly tests walk `testdata/linux/decompile/<arch>` and run only on Linux hosts with available compiler support.

State and persistence: tests read fixture files and may write expected outputs only when the package-level `-update` flag is set. Otherwise they are deterministic and in-memory. Fake module metadata lets module symbolization run without real kernel binaries.

Dependencies and integration points: depends on `targets`, `mgrconfig`, `symbolizer`, `vminfo`, `osutil`, `testify/assert`, and runtime host OS checks. It exercises public reporter APIs plus Linux internals, so refactors must preserve helper semantics or adjust tests deliberately.

Risks: tests are exact-output sensitive, especially file-line formatting and decompiled instruction text. Disassembly tests depend on host platform and cross-toolchain availability. Some branches in the large oops table are only covered by external fixtures, not this file.

Test signals: failures identify regressions in title suppression, report boundaries, prefix stripping, symbol/module lookup, inline frame rendering, opcode endian handling, and decompiler integration. Run with `go test ./pkg/report`; run on Linux for full disassembly coverage.
