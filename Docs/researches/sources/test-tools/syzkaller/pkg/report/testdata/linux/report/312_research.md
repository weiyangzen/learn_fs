# sources/test-tools/syzkaller/pkg/report/testdata/linux/report/312

Purpose: Linux reporter fixture for syzkaller; expected parsed title is `memory leak in map_create` and the expected crash type is `LEAK`. Memory leak in BPF map creation: per-CPU allocator frames lead through `htab_map_alloc` into `map_create` from the `bpf` syscall.

Important APIs, types, and functions: this is data consumed by the syzkaller `pkg/report` test harness rather than executable Go code. `report_test.go` reads this file with `parseReport`, strips carriage returns, parses `TITLE`, `ALT`, `TYPE`, `CORRUPTED`, `PANICKED`, and related headers, then compares the expected values with `Reporter.Parse`, `ContainsCrash`, and `ParseFrom`. The fixture exercises the Linux reporter implementation in `linux.go`, generic `Report` fields from `report.go`, and crash type mapping through `crash.TitleToType`.

Control flow: the test runner enumerates `pkg/report/testdata/linux/report`, constructs a Linux reporter, loads this fixture, separates the leading expectation headers from the console log at the first blank line, and parses the remaining log bytes. For this file, expected parsed title is `memory leak in map_create`; alternate titles are none; extra parsed flags are none. The body is 21 lines and 928 bytes, so the parser sees the complete diagnostic shape rather than a sampled stack.

State and persistence behavior: the fixture is static testdata. It persists no runtime state, but it encodes expected parser state in header fields and the raw kernel-console transcript. The relevant transient parser state is the detected title, alternate titles, crash type, corrupted/panicked flags, report byte range, skip position, and executor metadata when present.

Dependencies and integration points: kmemleak output, BPF hash map allocation, percpu allocator, `__x64_sys_bpf`.. At repository level, the integration point is `TestParse` in `pkg/report/report_test.go`, with Linux-specific matching rules and oops tables in `pkg/report/linux.go`; syzkaller managers depend on the same parsing path to turn VM console output into deduplicated crash reports.

Risks and edge cases: this fixture can regress if Linux symbol names, syscall wrapper names, sanitizer wording, lockdep formatting, or reboot banners are matched too narrowly. The parser also has to ignore unrelated noise before, after, or inside the diagnostic, avoid over-preferring helper frames such as timer/RCU/watchdog functions, and preserve the expected corrupted or panicked classification when the stack is unreliable.

Test signals: the header values drive the expected parse result, the raw log must produce a non-empty `Report.Report`, and the parsed start/end positions must allow `ParseFrom` to rediscover the same report while skipping it after the report end.
