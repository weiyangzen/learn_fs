# File Research: sources/os/plan9/plan9/sys/src/cmd/vac/stdinc.h

Purpose: common include umbrella for Vac command sources.

Contents:
- Includes Plan 9 base headers: `<u.h>`, `<libc.h>`, `<bio.h>`, `<ctype.h>`, and `<thread.h>`.
- Includes Venti, security/hash, and regexp APIs: `<venti.h>`, `<libsec.h>`, and `<regexp.h>`.

Integration points:
- Used by most `cmd/vac` sources to keep include lists consistent.
