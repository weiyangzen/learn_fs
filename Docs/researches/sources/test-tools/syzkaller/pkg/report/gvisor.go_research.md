# Research: sources/test-tools/syzkaller/pkg/report/gvisor.go

Purpose: implements the gVisor reporter backend. It recognizes gVisor/Sentry panics, signals, fatal errors, data races, invalid partial-result messages, common Go runtime failures, and syzkaller common failures while suppressing known resource-exhaustion noise.

Important APIs/types/functions: `type gvisor` embeds `config`; `ctorGvisor` returns resource/OOM/PID-exhaustion suppressions; `ContainsCrash` and `Parse` delegate to shared `containsCrash` and `simpleLineParser`; `shortenReport` compacts enormous Go panic dumps; `Symbolize` is a no-op; `gvisorTitleReplacement` normalizes container/sandbox names and PIDs; `gvisorOopses` defines Panic, SIGSEGV, SIGBUS, FATAL ERROR, DATA RACE, partialResult, fatal error, and BUG-on patterns.

Control flow: parsing locates the first gVisor oops, extracts a title with no stack-specific frame extraction, applies gVisor-specific dynamic title replacements, and shortens the report to the first goroutine block. For data races, shortening keeps both relevant stacks by extending to a second blank-line block.

State and persistence: no persistent state. Suppressions and replacement tables are immutable process data; parsed reports hold raw output, normalized title, and compacted report bytes.

Dependencies and integration points: selected from `ctors` for `targets.GVisor`; shares `commonOopses`, `replacement`, `oops`, and `simpleLineParser` from `report.go`. Its output participates in generic syzkaller crash deduplication through normalized titles and `crash.TitleToType`.

Risks: Go panic formats change over time, and fixed five-line-plus-blank-block truncation can lose context for unusual panics. Normalizing all container/sandbox names and PIDs improves deduplication but can merge distinct environment-specific issues. Suppression rules for OOM/PID exhaustion must be kept aligned with gVisor runtime error text.

Test signals: parse fixtures in the shared `all` directory cover Go panic/SYZFATAL behavior that gVisor also consumes. Dedicated gVisor fixtures should include data race dual-stack preservation, container/sandbox title replacement, and each suppression string.
