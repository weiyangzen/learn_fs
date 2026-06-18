# Research: sources/test-tools/syzkaller/pkg/report/netbsd_test.go

Purpose: verifies NetBSD-specific symbolization patterns supplied to the shared BSD reporter.

Important APIs/types/functions: `TestNetbsdSymbolizeLine` builds a table of `symbolizeLineTest` cases and delegates to `testSymbolizeLine` with `ctorNetbsd`. Cases include regular stack frames, inline frames, missing symbols, and witness lines with one- and two-digit frame indexes.

Control flow: the shared BSD test helper constructs a reporter with fake symbol data and checks that NetBSD regexps identify the function/offset region where file:line data should be inserted.

State and persistence: no persistence; all symbol data is test-local.

Dependencies and integration points: depends on `bsd_test.go` helpers and the NetBSD constructor. It indirectly guards `bsd.symbolizeLine` against changes that would break NetBSD's `netbsd:` prefix handling.

Risks: it only tests symbolization, not NetBSD oops detection/title extraction. Regex changes that still pass these narrow cases can still miss real panic formats.

Test signals: failures point to broken NetBSD stack or witness frame symbolization.
