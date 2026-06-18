# sources/test-tools/syzkaller/pkg/report/darwin.go

Purpose: Defines Darwin crash reporter construction and Darwin-specific oops patterns.

Important APIs and data: `ctorDarwin` calls `ctorBSD` with `darwinOopses` and no symbolization regexes. `darwinOopses` matches `panic(cpu ...)` forms, assertion failures, kernel traps, known route/zalloc panic formats, generic quoted/unquoted panics, debugger unexpected trap numbers, Go runtime errors, and common oopses.

Control flow and state: Runtime behavior is inherited from `bsd`: `ContainsCrash`, `Parse`, and symbolization support. Since `symbolizeRes` is empty, line symbolization will not modify Darwin reports through this constructor.

Dependencies and integration: Registered through the report package constructor map in `report.go` (outside this shard). Uses shared oops parsing helpers and BSD implementation.

Risks: Regex ordering matters; generic panic patterns can catch titles that might deserve more specific handling. No symbolization regexes means Darwin reports depend on raw logs for source detail.

Test signals: No direct Darwin test in this shard; BSD helper can support platform tests elsewhere.
