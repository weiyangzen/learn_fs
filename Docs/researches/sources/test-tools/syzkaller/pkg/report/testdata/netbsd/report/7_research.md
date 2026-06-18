# sources/test-tools/syzkaller/pkg/report/testdata/netbsd/report/7

## Purpose

This tiny NetBSD fixture contains no `TITLE:` metadata and consists of a syslog-looking login line that includes `postfix/pickup[596]: panic: event_init: unable to initialize`. Its purpose is negative coverage: the reporter should not classify arbitrary userland syslog text as a kernel crash.

## Important APIs, Types, and Functions

The relevant syzkaller APIs are `Reporter.ContainsCrash` and `Reporter.Parse` for NetBSD report detection. There are no kernel stack frames, DDB commands, or executable source APIs in the file. The important token is the literal word `panic:` embedded in a daemon log line.

## Control Flow

The parser receives a two-line input, sees no expected title, and must distinguish a syslog facility/program message from a kernel panic transcript. There is no traceback, no `Stopped in pid`, no `cpuN: Begin traceback`, no DDB prompt, and no dump/reboot boundary.

## State and Persistence Behavior

The only persisted state is the syslog timestamp, hostname, process name, process ID, and message. Parser state should remain empty for crash extraction. No kernel state is represented.

## Dependencies and Integration Points

This integrates with false-positive filtering for NetBSD logs that include the word `panic` outside kernel context. It protects syzkaller dashboards from ingesting service startup failures as kernel bugs.

## Risks and Edge Cases

The risk is overmatching on `panic:` alone. A parser that ignores syslog prefixes or process names would produce a bogus title and report. The case also checks that missing `TITLE:` is acceptable for a no-crash fixture.

## Test Signals

A passing test reports no crash or yields an empty parsed result, depending on harness convention. It should not create `panic: event_init: unable to initialize` as a kernel title.
