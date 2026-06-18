# File Research: sources/os/plan9/plan9/sys/src/cmd/aquarela/nbss.c

Implements NetBIOS session service over TCP port `netbios`.

Key functions:
- `nbsslisten` announces TCP NetBIOS service and registers called/calling name accept filters.
- `tcpreader` parses NBSS frames, handles session requests, positive/negative responses, keepalives, and session messages.
- `nbssconnect` resolves a NetBIOS name, dials TCP, sends a session request, and validates the response.
- `nbssgatherwrite` and `nbssscatterread` frame and unframe SMB payloads.
- `nbsswrite`, `nbssread`, and `nbssfree` are simple public wrappers.

Interactions:
- Server path feeds accepted SMB payloads to `smbsessionwrite` via `aquarela.c`.
- Client path used by `smbconnect.c`.

Notable details:
- Session request matching distinguishes called-name-not-present from called-name-present/calling-name-not-listened errors.
- Supports 17-bit NBSS length via low bit in flags.
