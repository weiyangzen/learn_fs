# sources/test-tools/syzkaller/pkg/manager/report_generator.go

Purpose: Wraps lazy initialization and caching of `cover.ReportGenerator` for coverage reports, with explicit module initialization and reset support.

Important APIs and types: `ReportGeneratorWrapper` stores manager config, kernel modules, a mutex, initialization flag, and cached generator. `ReportGeneratorCache` constructs the wrapper. `Get` returns a cached or newly created generator. `Init` records modules and marks initialized. `Reset` drops the cached generator. `CoverToPCs` converts raw coverage PCs to previous-instruction PCs.

Control flow and state: `Get` locks, rejects calls before `Init`, and lazily calls `cover.MakeReportGenerator`. `Init` panics on double initialization to catch inconsistent module discovery. `Reset` is used by HTTP coverage `flush` to force rebuilding and release memory. `CoverToPCs` loops raw PCs through `backend.PreviousInstructionPC` using the target and VM type from config.

Dependencies and integration: Used by `kernelContext.CoverageFilter` to initialize filters and by HTTP coverage handlers to generate HTML/text/JSONL coverage reports. Depends on `cover`, `cover/backend`, `mgrconfig`, `vminfo`, and logging.

Risks: Double `Init` panic is intentional but can crash the manager if module setup is retried. `Get` serializes generator creation and may block coverage requests. Reset while another caller uses a returned generator is safe for the pointer but can increase memory churn.

Test signals: No direct tests in this shard; exercised indirectly by manager coverage paths and HTTP template coverage.
