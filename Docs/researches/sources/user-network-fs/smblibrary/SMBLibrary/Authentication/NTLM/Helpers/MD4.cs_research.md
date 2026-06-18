<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/Authentication/NTLM/Helpers/MD4.cs -->
# sources/user-network-fs/smblibrary/SMBLibrary/Authentication/NTLM/Helpers/MD4.cs

## Purpose
`MD4` is a bundled MD4 digest implementation used to compute NT hashes for NTLM. It lives under `System.Security.Cryptography` for local convenience.

## Important APIs and Types
Public helpers compute byte or hex hashes from strings, bytes, or a single byte. Internally `EngineUpdate()`, `EngineDigest()`, and `Transform()` implement RFC 1320 padding, block buffering, and the three MD4 rounds.

## Control Flow
Input bytes are buffered into 64-byte blocks. Finalization appends `0x80`, zero padding to 56 mod 64, and the little-endian bit length. `Transform()` decodes 16 little-endian 32-bit words, applies FF/GG/HH rounds, and accumulates context state. Each public hash method uses a fresh `MD4` instance and resets after digest.

## State, Dependencies, and Integration
State is instance-local: four context words, a 64-byte buffer, a 16-word work array, and byte count. `NTLMCryptography.NTOWFv1()` and session-base-key derivation depend on this exact MD4 behavior.

## Risks and Test Signals
MD4 is cryptographically obsolete but required by NTLM. The string helper uses UTF-8, while NTLM callers correctly pass UTF-16LE bytes themselves. Tests should use RFC 1320 MD4 vectors and NTLM NTOWF vectors, including empty string and long multi-block inputs.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/Authentication/NTLM/Helpers/MD4.cs -->
