# sources/sync-backup/git-lfs/tools/os_tools.go

Purpose: working-directory and Cygwin path translation helpers.

Important APIs/types/functions: `Getwd`, `translateCygwinPath`, and `TranslateCygwinPath`.

Control flow: `Getwd` calls `os.Getwd`, then translates through `cygpath -w` when running under Cygwin. Translation uses `subprocess.ExecCommand`, forces `LC_ALL=C.UTF-8`, captures stderr, tolerates missing `cygpath`, and wraps real conversion failures.

State and persistence: no durable state; invokes a subprocess and reads environment.

Dependencies and integration points: used by path canonicalization flows in `filetools.go`; relies on `isCygwin` from another platform file and Git LFS `subprocess`, `tr`, and pkg/errors.

Risks: external `cygpath` behavior and locale availability affect output. Missing executable is silently tolerated, which is intentional but can mask misconfigured Cygwin environments.

Test signals: not directly covered in this subset.
