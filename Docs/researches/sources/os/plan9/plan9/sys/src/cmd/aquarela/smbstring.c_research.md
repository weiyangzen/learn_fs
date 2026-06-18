# File Research: sources/os/plan9/plan9/sys/src/cmd/aquarela/smbstring.c

Implements SMB string sizing, decoding, duplication, formatting, and wire encoding helpers.

Key points:
- `smbruneconvert` applies SMB path slash conversion, uppercasing, and optional space/non-breaking-space mapping.
- `smbstringlen`, `smbucs2len`, and `smbstrlen` choose wire length by peer Unicode capability and global Unicode mode.
- `smbstringdup` reads either ASCII NUL-terminated strings or aligned UCS-2 strings from SMB byte data.
- `smbstrput`, `smbucs2put`, and `smbstringput` serialize strings with optional Unicode/ASCII forcing, alignment, termination, case conversion, and path conversion.
- `smbstringprint` owns and replaces dynamically formatted error/message strings.

Dependencies and interactions:
- Uses `SmbPeerInfo`, `SmbHeader`, SMB string flags, `smbglobals`, and Plan 9 rune conversion helpers.
- Central utility for Aquarela packet parsers and encoders.

Notable behavior:
- UCS-2 decode advances to even alignment relative to a base pointer.
- `smbucs2put` asserts writes remain within the caller-provided max length.
