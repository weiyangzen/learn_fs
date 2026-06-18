# sources/test-tools/syzkaller/pkg/stat/syzbotstats/bug.go

## Purpose

`bug.go` defines the compact summary model for syzbot bug statistics.

## Important APIs, Types, And State

`BugStatSummary` records title, syzbot IDs, first/released/repro/cause-bisect/resolved times, status, subsystems, strace availability, hit rate, fix hashes, and managers where the bug happened. `BugStatus` is a string enum with values `fixed`, `invalidated`, `auto-invalidated`, `dup`, and `pending`.

## Dependencies, Integration, Risks, And Test Signals

The only dependency is `time.Time`. The struct is designed for serialization/reporting by syzbot statistics code outside this file. Risks are semantic drift in status strings, zero `time.Time` values representing absent milestones, and consumers needing to treat `IDs`, `FixHashes`, and `HappenedOn` as sets despite slice representation. There are no direct tests here; schema compatibility and downstream stats rendering are the signals.
