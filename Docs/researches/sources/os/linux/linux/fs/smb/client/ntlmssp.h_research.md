# File Research: sources/os/linux/linux/fs/smb/client/ntlmssp.h

## Purpose
Defines NTLMSSP wire constants, flags, AV-pair identifiers, packed message structures, and prototypes for NTLMSSP negotiate/challenge/authentication blob helpers.

## Main Contents
- NTLMSSP signature and message type constants for negotiate, challenge, authenticate, and unknown messages.
- Negotiate flags for Unicode/OEM strings, signing, sealing, NTLM, target info, version, 128-bit, key exchange, and 56-bit support.
- `enum av_field_type` for target-info AV pairs such as NetBIOS/DNS names, flags, timestamp, target name, restrictions, and channel bindings.
- Packed `SECURITY_BUFFER`, negotiate-message, challenge-message, and authenticate-message layouts.
- `struct ntlmssp_version` for MS-NLMP version fields.
- Prototypes for challenge decoding and negotiate/auth blob construction.

## Integration Points
Used by NTLMSSP authentication implementation and CIFS encryption/auth helpers. The structures match MS-NLMP/NTLMSSP wire format and are consumed when building SMB session setup security blobs.

## Notable Behaviors
- Older typedef-style structures are retained to mirror NTLMSSP standards.
- SMB3 negotiate blob construction can include version information while the older negotiate layout omits it.
- All wire structures are packed and use little-endian fields.

## Risks And Review Focus
- Wire layout and packing are security-sensitive because auth blobs are parsed by servers and local crypto code.
- Flag definitions must stay compatible with NTLMSSP negotiation behavior and FIPS/auth policy in implementation files.
