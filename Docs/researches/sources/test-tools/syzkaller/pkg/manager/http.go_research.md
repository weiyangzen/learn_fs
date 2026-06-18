# sources/test-tools/syzkaller/pkg/manager/http.go

Purpose: Implements the syz-manager HTTP dashboard and API surface for runtime status, crashes, corpus, coverage, VM state, job state, raw files, and patch-diff fuzzing summaries.

Important APIs and types: `HTTPServer` owns config, start time, crash/diff stores, repro loop, VM pools, pause callback, and atomic pointers for corpus, fuzzer, coverage, and enabled syscalls. `CoverageInfo` carries modules, report generator, and executor cover filter. UI data types include `UISummaryData`, `UICrashType`, `UIDiffBug`, `UIVMData`, `UISyscallsData`, `UICorpusPage`, `UIRawCoverPage`, and `UIJobList`.

Control flow: `Serve` registers compressed handlers on the default HTTP mux and shuts down when context ends. `httpMain` builds the summary page from stats, crash store, repro loop, subsystem filters, and diff store. `httpAction` toggles expert/pause state and redirects through `localRedirectURL` to prevent open redirects. Config/stats/syscalls/VM handlers render JSON or templates. Corpus handlers list, download, fetch, and debug inputs. Coverage handlers require initialized coverage and corpus, build `cover.HandlerParams`, optionally filter PCs, serialize programs, and dispatch to report-generator methods for HTML/text/JSONL outputs. File/report handlers restrict ids/paths and expose saved crash artifacts. `httpAddCandidate` accepts multipart seed uploads and adds enabled-call-only candidates to the fuzzer. Diff handlers classify store entries into patched-only, affects-both, and in-progress tables. Job handlers expose running fuzzer job details.

State and persistence: The server reads persistent crash/corpus files from `Cfg.Workdir`, but mostly presents atomic in-memory manager state. It can reset cached coverage generator on `flush` and mutate pause/expert flags.

Dependencies and integration: Integrates `corpus`, `cover`, `fuzzer`, `html/pages`, `prometheus`, `report`, `stat`, `vcs`, `prog`, `vm/dispatcher`, crash store, diff store, and report generator cache.

Risks: Uses global `http.Handle`, so multiple servers in one process can collide. `httpAddCandidate` assumes `Fuzzer.Load()` is non-nil. `httpFile` allows only `crashes/` and `corpus/` prefixes after `filepath.Clean`, but path traversal must remain carefully reviewed. Coverage generation can be expensive; large program serialization strips filesystem images after 100 MB.

Test signals: `http_test.go` executes all registered templates with random data and checks redirect hardening.
