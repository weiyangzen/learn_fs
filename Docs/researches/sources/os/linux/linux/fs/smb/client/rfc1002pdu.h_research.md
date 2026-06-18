# File Research: sources/os/linux/linux/fs/smb/client/rfc1002pdu.h

This header defines RFC 1001/1002 NetBIOS session-service packet constants and the packed session packet layout used by CIFS/SMB transport code.

Key contents:
- Session packet type constants: session message, request, positive/negative response, retarget response, and keepalive.
- `RFC1002_LENGTH_EXTEND` marks the high-order length bit for payloads over 64 KiB.
- `struct rfc1002_session_packet` models the big-endian NetBIOS session header and its variants:
  - session request called/calling names,
  - retarget response address/port,
  - negative-session-response error code,
  - message trailers that carry SMB/CIFS payloads.
- Negative response codes are defined for not-listening, called-name-not-present, insufficient-resource, and unspecified-error cases.
- `DEFAULT_CIFS_CALLED_NAME` is the default NetBIOS called name string.

Important note:
- Unlike SMB/CIFS packets, these RFC1002 structures are big-endian. Code touching this header must preserve that endian distinction.
