## sources/security-integrity/libcap/goapps/captree/captree.go

Purpose: process-tree inspection tool that displays capabilities and IAB state for processes and threads rooted at supplied PIDs or command-name globs.

Important APIs/types/functions: flags `--proc`, `--depth`, `--verbose`, `--color/--colour`; `task` struct; functions `isATTY()`, `highlight()`, `(*task).fill()`, `rDump()`, `findPIDs()`, `setDepth()`, and `main()`. Uses `cap.GetPID`, `cap.IABGetPID`, `cap.ProcRoot`, `Set.Cf`, and `IAB.Cf`.

Control flow: reads all numeric directories under proc root, concurrently fills each process with status name/parent, capabilities, IAB, and thread details, builds parent-child relationships and depths, resolves requested PIDs/globs, then recursively dumps a tree with compact thread grouping when caps/IAB/name match.

State/persistence: in-memory task graph only; reads `/proc` or an alternate proc root.

Dependencies/integration: Go cap package, Linux procfs status/task layout, terminal color detection. Built and installed by `go/Makefile`.

Risks: process churn causes zombie/missing status races; a visible code issue parses `pid` instead of `tid` when filling thread capability state, which can under-report thread differences; recursive `setDepth` assumes parent entries exist except kernel root.

Test signals: `./captree 0`, `./captree $$`, `./captree --proc <fixture>`, thread-difference fixtures, and `go/Makefile` running `./captree 0`.
