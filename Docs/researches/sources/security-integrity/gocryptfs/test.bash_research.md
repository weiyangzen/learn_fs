# sources/security-integrity/gocryptfs/test.bash

Purpose: Shell utility in the shell harness area for testing, benchmarking, profiling, packaging, or cleanup.

Important APIs and types: Shell entry points `unmount_leftovers`. External commands observed: gocryptfs, go test, go vet, staticcheck, shellcheck, tar, ls, rm.

Control flow: The script runs in strict shell mode where present, prepares paths or validates arguments, invokes gocryptfs or filesystem utilities, and relies on exit status for success/failure.

State and persistence behavior: May create temporary directories, lock files, mounts, release tarballs, profile files, benchmark data, or downloaded tarballs; cleanup is handled by traps or later harness steps when present.

Dependencies and integration points: `gocryptfs`, `go test`, `go vet`, `staticcheck`, `shellcheck`, `tar`, `ls`, `rm`

Risks: panic paths are intentional for programmer errors but must not be reachable from untrusted malformed ciphertext except where tests expect ordinary errors; platform syscall semantics and kernel/FUSE differences can change behavior; scripts are environment-sensitive and can leave mounts or temporary files if interrupted before cleanup.

Test signals: Signal is successful script completion and expected command output/artifacts; several scripts are manual benchmark/profile helpers rather than deterministic tests.
