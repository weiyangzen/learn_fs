## sources/test-tools/syzkaller/pkg/manager/covfilter.go

Purpose: builds coverage PC filters and focus areas for syz-manager/fuzzer execution.

Important APIs/types/functions: `CoverageFilter`, `covFilterAddFilter`, `covFilterAddRawPCs`, `compileRegexps`, `CoverageFilters`, and `PrepareCoverageFilters`.

Control flow: if filter config is non-empty, obtains a report generator, matches function regexps against symbols and file regexps against units, adds both PCs and comparison PCs, adds raw PCs from files, and optionally errors when strict filters match nothing. Focus area preparation converts filter PCs to KCOV next-instruction PCs and builds an executor-wide filter when all focus areas are filtered.

State and persistence: reads raw PC files; logs matched filter units. Returns in-memory PC maps and focus areas.

Dependencies and integration: depends on `ReportGeneratorWrapper`, coverage backend object units, manager config focus areas, corpus focus areas, and target-specific `NextInstructionPC`.

Risks: raw PC parser regex only accepts lowercase hex. `defer rawFile.Close()` in a loop delays closes until function return. Strict mode checks regexps, not individual focus areas. Empty focus filter disables executor filtering by design.

Test signals: no direct tests in this subset; behavior is indirectly exercised by manager/diff coverage workflows.
