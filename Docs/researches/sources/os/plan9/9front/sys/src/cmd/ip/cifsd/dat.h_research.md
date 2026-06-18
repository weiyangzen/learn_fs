# File Research: sources/os/plan9/9front/sys/src/cmd/ip/cifsd/dat.h

Defines core data structures, globals, and constants for `cifsd`.

Key points:
- Defines `Rop` string/name packing operations for ASCII vs Unicode SMB modes.
- Defines `Req` for a single SMB request: command ids, tid/pid/uid/mid, flags, signature, response buffer pointers, packing ops, request name, response callback, and name comparison function.
- Defines `Trans` for SMB transaction requests with parameter/data/setup input and output buffers.
- Defines `File`, `Find`, `Share`, and `Tree` server state structures.
- Declares global configuration/state: debug, space translation, auth requirement, domain, program/OS names, remote system/user, buffer size, start time, timezone offset.
- Defines NT status codes, resource/share types, capability flags, DOS attributes, file access masks, share access modes, create dispositions/actions/options, and buffer size.

Dependencies and interactions:
- Shared by all `cifsd` implementation files.
- `Idmap` is forward-declared and implemented in `idmap.c`.

Research relevance:
- This is the central protocol/server-state contract for the CIFS/SMB server.
