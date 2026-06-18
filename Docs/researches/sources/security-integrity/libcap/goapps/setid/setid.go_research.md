## sources/security-integrity/libcap/goapps/setid/setid.go

Purpose: demonstration tool for changing UID/GID/supplementary groups across all Go runtime threads using either cap convenience APIs or raw psx syscalls.

Important APIs/functions: flags `--uid`, `--gid`, `--drop`, `--suppl`, `--caps`; functions `setIDsWithCaps()`, `splitToInts()`, `dumpStatus()`, and `showIDs()`. Uses `cap.SetGroups`, `cap.SetUID`, `cap.NewSet().SetProc`, `psx.Syscall3`, and `/proc/<pid>/task/*/status`.

Control flow: records before state, parses target IDs and supplementary groups, changes IDs via cap or psx path, optionally drops all capabilities, then scans every task status to validate all threads show expected Uid/Gid lines.

State/persistence: mutates process UID/GID/groups and capabilities; no persistent files.

Dependencies/integration: Go cap and psx packages, Linux procfs task status, privilege to change IDs. Built/run by `go/Makefile`.

Risks: raw psx setgroups call appears to pass pointer where Linux syscall expects count as first argument on many ABIs, so `--caps=false` may be limited/bug-prone; supplementary groups are not fully validated in output; privilege changes are irreversible.

Test signals: `./setid --caps=false` from `make -C go test`, plus privileged runs with explicit UID/GID/group combinations.
