# File Research: sources/os/linux/linux-stable/fs/smb/client/ntlmssp.h

Read status: complete.

## Purpose

Defines NTLMSSP constants, wire-format message structures, AV-pair identifiers, version layout, and authentication blob helper prototypes for CIFS NTLM/NTLMSSP authentication.

## Main Contents

- NTLMSSP signature and message type constants:
  - Negotiate, Challenge, Authenticate, and Unknown.
- NTLMSSP negotiate flag definitions:
  - Unicode/OEM, target request/type, signing/sealing, NTLM, anonymous, supplied domain/workstation, extended security, target info, version, 128-bit, key exchange, and 56-bit support.
- `enum av_field_type`
  - Defines NTLMSSP target-info AV pair ids such as NetBIOS names, DNS names, flags, timestamp, target name, and channel bindings.
- `SECURITY_BUFFER`
  - Packed length/maximum-length/offset descriptor used in NTLMSSP messages.
- `NEGOTIATE_MESSAGE`
  - Legacy negotiate layout without version block.
- `struct ntlmssp_version`
  - MS-NLMP version field with product version, module build, reserved bytes, and NTLM revision.
- `struct negotiate_message`
  - SMB2+ negotiate layout including version.
- `CHALLENGE_MESSAGE`
  - Server challenge layout with target name, negotiate flags, challenge bytes, reserved field, and target-info array.
- `AUTHENTICATE_MESSAGE`
  - Client authenticate layout with LM/NT challenge responses, domain, user, workstation, session key, flags, version, and trailing payload.
- Function prototypes:
  - `decode_ntlmssp_challenge()`
  - `build_ntlmssp_negotiate_blob()`
  - `build_ntlmssp_smb3_negotiate_blob()`
  - `build_ntlmssp_auth_blob()`

## Dependencies

- Uses CIFS crypto key size constants and CIFS session/server structures from surrounding CIFS headers.
- Implemented by NTLMSSP authentication code elsewhere in the SMB client.

## Notable Behaviors

- Structures are packed to match wire format.
- Typedefs are intentionally used here to mirror NTLMSSP standards terminology.
- SMB2+ negotiate messages can include the NTLMSSP version block while the legacy negotiate typedef omits it.
