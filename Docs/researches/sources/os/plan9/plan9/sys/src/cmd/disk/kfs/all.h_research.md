# File Research: sources/os/plan9/plan9/sys/src/cmd/disk/kfs/all.h

This is the umbrella include for KFS source files.

Contents:
- Includes Plan 9 base headers `u.h` and `libc.h`.
- Includes local `dat.h` and `fns.h`.
- Includes system protocol/auth headers `<fcall.h>`, `<auth.h>`, and `<authsrv.h>`.

Role:
- Centralizes the dependency set for KFS implementation files.
- Pulls in both local disk/server data structures and Plan 9 9P/auth APIs.
