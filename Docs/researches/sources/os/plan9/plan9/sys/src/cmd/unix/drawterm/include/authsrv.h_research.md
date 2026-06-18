# File Research: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/include/authsrv.h

Drawterm copy of Plan 9 libauthsrv wire-format and authentication-server interface.

Key contents:
- Defines authentication protocol constants, legacy name/key lengths, DES key lengths, challenge sizes, and auth message type numbers.
- Defines wire structures for ticket requests, tickets, authenticators, password requests, old CHAP/MSCHAP replies, and NVRAM safe storage.
- Declares conversion routines between structs and wire buffers, DES password-key conversion helpers, NVRAM read helpers, auth server dialing, ticket exchange, and SSL negotiation helpers.

Role in this group:
- Supplies the old Plan 9 authentication protocol ABI used by drawterm authentication code.

Notable risks:
- The protocol definitions are DES-centered and include legacy compatibility formats.
- Fixed-width name fields such as `ANAMELEN` reflect old protocol constraints.
