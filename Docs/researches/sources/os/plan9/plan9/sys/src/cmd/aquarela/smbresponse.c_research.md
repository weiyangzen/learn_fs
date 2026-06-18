# File Research: sources/os/plan9/plan9/sys/src/cmd/aquarela/smbresponse.c

Thin response-buffer API for `SmbSession`.

Key functions:
- `smbresponseinit`, `smbresponsereset`, and write helpers delegate to `SmbBuffer`.
- `smbresponseputheader`, `smbresponseputandxheader`, and `smbresponseputerror` build common response headers.
- `smbresponsesend` logs outgoing packet data and writes it through either NBSS scatter/gather or direct CIFS framing.

Interactions:
- Used by command handlers that prefer session-level response helpers over raw `smbbuffer` calls.

Notable details:
- Direct CIFS responses write a 4-byte big-endian-ish NetBIOS length prefix through `hnputl`.
