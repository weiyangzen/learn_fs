# File Research: sources/os/plan9/plan9/sys/src/cmd/aquarela/smbservice.c

SMB share/service registry and lookup.

Key data:
- Built-in `IPC$` service for IPC.
- Built-in `local` disk tree service rooted at `/n/local`.

Key functions:
- `run9fs` forks `/rc/bin/9fs <share>` and waits for completion.
- `smbservicefind` parses UNC paths, accepts IPC, local, and session-specific shares, and can dynamically run `9fs` to create `/n/<share>` then register a session service.
- `smbserviceget`/`smbserviceput` adjust service refs.

Interactions:
- Used by tree connect handler and RAP share enumeration.

Notable details:
- Server-name validation in UNC path is present but commented out.
