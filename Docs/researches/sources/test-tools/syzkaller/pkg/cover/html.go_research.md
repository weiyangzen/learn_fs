# sources/test-tools/syzkaller/pkg/cover/html.go

Purpose: implements coverage report output handlers: HTML, line JSON, raw coverage, raw frame CSV, per-file/function CSV summaries, subsystem/module tables, coverage JSONL, and per-program coverage JSONL.

Important APIs/types/functions: `HandlerParams`, `DoHTML`, `DoLineJSON`, `DoRawCoverFiles`, `CoverageInfo`, `DoCoverJSONL`, `ProgramCoverage`/`FileCoverage`/`FuncCoverage`/`Block`, `DoCoverPrograms`, `DoRawCover`, `DoFilterPCs`, `convertToStats`, `DoFileCover`, `DoSubsystemCover`, `DoModuleCover`, `DoFuncCover`, `fixUpPCs`, `fileContents`, `perLineCoverage`, `mergeRange`, `mergeLine`, `addFunctionCoverage`, `processDir`, `Percent`, and `parseFile`.

Control flow: handlers first filter/fix PCs and prepare file maps through `ReportGenerator`. HTML builds a directory tree, renders source files with span classes for covered/uncovered/both chunks, adds program click metadata, and executes embedded templates. JSONL handlers symbolize callback and program PCs, aggregate frames by PC/file/function, and stream JSON records. CSV/table handlers compute per-file stats and aggregate by subsystem prefixes or module names.

State and persistence: reads source files and embedded templates; writes only to the provided `io.Writer`. `ReportGenerator` frame cache may grow as symbolization is requested.

Dependencies and integration: depends on `backend` range/frame data, `mgrconfig.Subsystem`, embedded templates, and `report.go` file maps. Outputs feed syzkaller web endpoints and CI export paths.

Risks: `DoHTML` assumes `progs[0]` exists when computing `haveProgs`; empty program input can panic. `fileLineContents` has a `start` variable that is not advanced, which can duplicate line classification work. File links and query-like data are mostly template/html escaped but CSV consumers depend on schema stability. `Percent` deliberately caps partial coverage at 99.

Test signals: `cover_test.go` validates range merging; `report_test.go` exercises HTML, CSV, JSONL, and subsystem/file/function outputs through compiled binaries.
