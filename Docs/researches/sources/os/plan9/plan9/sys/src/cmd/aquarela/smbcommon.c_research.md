# File Research: sources/os/plan9/plan9/sys/src/cmd/aquarela/smbcommon.c

Common SMB header, error, chaining, attribute, and lookup-table helpers.

Key functions:
- `smbsendunicode` checks global and peer Unicode capability.
- `smbcheckwordcount` and `smbcheckwordandbytecount` validate request shape.
- `smbchaincommand` moves the request buffer to an AndX offset and dispatches the chained command.
- `smbbuffergetheader` parses `SmbRawHeader`, validates protocol, fills `SmbHeader`, and pushes byte-count read limit.
- `smbbufferputheader`, `smbbufferputandxheader`, `smbbufferputerror`, and `smbbufferputack` build response headers.
- Attribute helpers translate between Plan 9 modes and DOS attributes.
- `smbl2roundupvlong` rounds file sizes to allocation units.
- `smbslut` and `smbrevslut` map string/value tables.

Interactions:
- Used by all SMB command and client paths.

Notable details:
- `smbdosattr2plan9wstatmode` tries to preserve old mode bits when only attributes change.
- Provides global share/open mode lookup tables.
