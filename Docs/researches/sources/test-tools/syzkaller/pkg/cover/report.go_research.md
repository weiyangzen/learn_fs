# sources/test-tools/syzkaller/pkg/cover/report.go

Purpose: owns the core conversion from raw program PCs to file/function/line coverage structures consumed by HTML, CSV, JSON, and raw report handlers.

Important APIs/types/functions: `ReportGenerator`, `Prog`, `GetPCBase`, `MakeReportGenerator`, internal `file`, `function`, `line`, `fileMap`, `prepareFileMap`, `frame2line`, `coverageCallbackMismatch`, `uniquePCs`, `symbolizePCs`, `fileByFrame`, and `findSymbol`.

Control flow: `MakeReportGenerator` builds a backend `Impl` and appends an `all` subsystem. `prepareFileMap` symbolizes unique program PCs, creates files from compile units, maps PCs to program indexes, checks callback-point membership when precise coverage is enabled, converts frames to covered/uncovered line ranges, computes per-file and per-function PC counts, and sorts functions. `symbolizePCs` finds containing symbols for requested PCs and symbolizes whole symbols once, caching frames and marking symbols.

State and persistence: `ReportGenerator` stores backend data and grows `Frames`; `Symbol.Symbolized` mutates in backend symbols. No files are written here.

Dependencies and integration: depends on `backend.Impl`, `mgrconfig`, target metadata, and module metadata. All report output functions in `html.go` call into this file.

Risks: `findSymbol` uses `pc > s.End` rather than `pc >= s.End`, while symbol ranges elsewhere are `[Start, End)`, creating a boundary inconsistency. Strict callback mismatch errors depend on accurate `CallbackPoints`; module/KASLR issues surface here. `frame2line` fails if no frame matches any covered PC.

Test signals: `report_test.go` is the major integration test, compiling binaries and checking HTML/CSV/JSONL paths and error cases.
