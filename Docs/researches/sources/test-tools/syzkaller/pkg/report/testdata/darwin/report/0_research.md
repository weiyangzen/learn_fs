# Research: sources/test-tools/syzkaller/pkg/report/testdata/darwin/report/0

Purpose: Darwin fixture expecting normalized title `panic: assertion failed: in6p == NULL || (in6p->inp_vflag & INP_IPV6)`. It validates XNU panic/debugger title extraction through the Darwin BSD-style reporter.

Important APIs/types/functions: the file is consumed by `report_test.go` through `forEachFile`, `readDir`, `parseReport`, `parseHeaderLine`, `testParseImpl`, and `checkReport`. It is data rather than Go code: metadata headers define expected `Report` fields, the blank-line-separated body is the raw console log, and an optional `REPORT:` block pins exact extraction.

Control flow: during `TestParse`, the relevant reporter for this fixture directory parses the raw log and `ContainsCrash` must agree with whether a title is expected. Parsed output is converted back into a `ParseTest` and compared with the headers. If a `REPORT:` section is present, `checkReport` also requires byte-for-byte equality for the shortened/extracted report. Start, end, and skip offsets are validated for every positive parse.

State and persistence: this fixture is static repository test data with 20 lines. It does not persist runtime state, but `go test ./pkg/report -update` can rewrite headers or expected report text when parser behavior is intentionally changed.

Dependencies and integration points: the fixture lives under the source-tree-aligned testdata hierarchy and is selected only because its basename is numeric. It integrates with the OS-specific reporter tables plus shared title sanitization, dynamic replacement, crash type classification, suppression handling, and report-boundary invariants. Expected crash type is `DoS`. No explicit corrupted/suppressed/panicked/executor flags are declared. The fixture has no explicit `REPORT:` block, so tests focus on metadata and parser invariants.

Risks: fixture expectations can become stale when kernel log formats, title sanitization, or oops ordering changes. Overly broad regexps may make a negative fixture positive; overly narrow regexps may lose this expected title. Exact report blocks are sensitive to trimming changes. First log signal: `panic(cpu 0 caller 0xffffff801f3ada45): assertion failed: in6p == NULL || (in6p->inp_vflag & INP_IPV6), file: /Users/space/kernel/xnu-7195.81.3/bsd/netinet6/in6_mcast.c, line: 1905`.

Test signals: a pass means the reporter still produces the expected title, type, flags, optional exact report body, and valid offsets for this sample. A failure should be reviewed against the responsible OS reporter table rather than blindly updating the fixture.
