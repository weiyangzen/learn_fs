# sources/user-network-fs/rclone/fs/march/march_test.go

## Purpose
`march_test.go` validates the lock-step traversal and matching behavior in `march.go` using local/mock filesystems and direct matching tests.

## Important APIs, types, and functions
The suite defines `marchTester`, which implements `Marcher`, and tests `March.Run`, `matchListings`, source/destination callbacks, error classification helpers, and transform-aware matching. It uses `fstest.Run`, local backend registration, `walk.ListR`, `list.NewSorter`, mock dirs/objects, and Unicode normalization.

## Control flow
`TestMarch` builds source-only, destination-only, and matched files/directories for several scenarios, configures no-traverse or fast-list, runs a `March`, and compares callback-collected entries against expected items. `TestMatchListings` constructs interleaved source/destination inputs, sorts them through `list.Sorter`, calls `matchListings`, and checks src-only, dst-only, and match outputs for duplicates, case transforms, Unicode transforms, and file/dir collisions.

## State and persistence behavior
Integration-style cases create temporary local/remote test files through `fstest.NewRun`. The tester stores callback entries and error state protected by mutexes. Fast-list tests temporarily monkey-patch local backend `ListR` and restore it.

## Dependencies and integration points
The tests exercise `march` together with `list.Sorter`, `walk.ListR`, filter config, local backend, mock object/dir packages, and rclone error classification. They reflect real sync traversal behavior more closely than isolated unit tests.

## Risks and edge cases
No-traverse matching only probes objects, not directories. Duplicate handling under transforms keeps the first stable-sorted entry. Unicode-equivalent names can collapse depending on normalization. The test comment says “swap src and dst” but repeats the same channel construction, so it mainly reruns the same assertion.

## Test signals
Coverage is strong for primary traversal modes, recursion decisions, depth behavior through directories, fast-list integration, transformed matching, duplicate skipping, and file/directory ordering semantics.

Source-read signal: reviewed complete local file (555 lines). Types observed: `marchTester`, `matchPair`. Functions/methods observed: `TestMain`, `DstOnly`, `SrcOnly`, `Match`, `processError`, `currentError`, `aborting`, `TestMarch`, `TestMatchListings`.
