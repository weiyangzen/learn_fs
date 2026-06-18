## sources/security-integrity/libcap/goapps/gowns/gowns.go

Purpose: experimental Go wrapper for launching a child with optional user namespace mappings, UID/GID changes, IAB values, and libcap capability mode.

Important APIs/types/functions: `nsDetail`, range type `r`, flags `--base`, `--uid`, `--gid`, `--iab`, `--mode`, `--ns`, `--uids`, `--gids`, `--shell`, `--verbose`; functions `ranges()`, `nsSetup()`, `parseRanges()`, and `main()`. Uses `cap.NewLauncher`, `Launcher.Callback`, `SetUID`, `SetGroups`, `SetIAB`, `SetMode`, `Launch`, and `cap.GetProc`.

Control flow: parses ID mappings, creates a launcher for the requested shell/args, optionally attaches a callback that configures `syscall.SysProcAttr` with `CLONE_NEWUSER` and mappings, sets UID/GID/IAB/mode options, raises effective `CAP_SETUID`/`CAP_SETGID` if permitted to support setup, launches, drops parent privileges to an empty set, and waits for the child.

State/persistence: mutates parent effective capabilities briefly, drops parent privileges, creates child namespace/credential state; no files.

Dependencies/integration: Go cap package launcher support, Linux user namespaces, proc/sysctl namespace policy, CAP_SETUID/CAP_SETGID for extended mappings.

Risks: marked unstable; namespace setup requires kernel support and may fail under distro restrictions; malformed range arguments fatal; parent privilege drop after launch is irreversible.

Test signals: `./gowns -- -c "echo gowns runs"` in normal tests and privileged namespace case in `go/Makefile sudotest`.
