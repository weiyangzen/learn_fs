# File Research: sources/os/plan9/plan9/sys/src/cmd/aquarela/aquarela.c

Main SMB/CIFS server entry point and per-session request dispatcher for Aquarela.

Key functions:
- `smbsessionwrite` parses an SMB request, validates session state, dispatches through `smboptable`, translates process results into SMB errors/replies, sends responses, and frees sessions on shutdown.
- `smbsessionfree` releases tree/search id maps, buffers, transaction storage, auth challenge state, and client strings.
- `nbssaccept` and `cifsaccept` allocate `SmbSession` objects for NetBIOS session service and direct CIFS transports.
- `logset` enables command-specific and subsystem debugging.
- `threadmain` parses options, initializes globals, starts direct CIFS listening, optionally starts NetBIOS service/listeners, and periodically sends browser host announcements.

Interactions:
- Central consumer of `smboptable`, `smbbuffer`, `smbresponse`, `nbss`, `smblisten`, `smbbrowse`, and authentication/session setup code.
- Uses id-map cleanup callbacks to close trees and searches.

Notable details:
- Only negotiate, session setup, tree connect, and echo are allowed before the session is established.
- Supports `-n` to enable NetBIOS in addition to direct CIFS.
