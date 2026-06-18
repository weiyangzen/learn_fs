# File Research: sources/os/plan9/plan9/sys/src/cmd/aquarela/smbbrowse.c

Builds SMB browser mailslot datagrams for host announcements.

Key functions:
- `smbmailslotsend` wraps a mailslot transaction and sends it over NetBIOS datagram transport.
- `smbbrowsesendhostannouncement` builds a browser host announcement message containing period, server name, version, server type, magic value, and comment.

Interactions:
- Called periodically by `aquarela.c` when NetBIOS mode is enabled.
- Uses `smbtransactionmethoddgram` and `nbdgramsend`.

Notable details:
- Sends to the primary domain name with NetBIOS type `0x1d`.
