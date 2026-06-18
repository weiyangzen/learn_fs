<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/Authentication/NTLM/Helpers/AuthenticationMessageUtils.cs -->
# sources/user-network-fs/smblibrary/SMBLibrary/Authentication/NTLM/Helpers/AuthenticationMessageUtils.cs

## Purpose
`AuthenticationMessageUtils` provides common NTLM message parsing helpers for security-buffer descriptors, signature checks, response-type detection, and message type extraction.

## Important APIs and Types
`ReadAnsiStringBufferPointer()`, `ReadUnicodeStringBufferPointer()`, and `ReadBufferPointer()` decode NTLM security buffers. `WriteBufferPointer()` writes length/max-length/offset descriptors. `IsSignatureValid()` checks `NTLMSSP\0`. `IsNTLMv1ExtendedSessionSecurity()`, `IsNTLMv2NTResponse()`, and `GetMessageType()` classify messages.

## Control Flow
Security-buffer readers read length, max length, and payload offset, returning empty arrays for zero length. Extended-session-security detection expects a 24-byte LM response with nonzero first 8 bytes and 16 zero padding bytes. NTLMv2 detection checks length and the two structure-version bytes at response offset 16.

## State, Dependencies, and Integration
The helper is stateless and used by every NTLM structure plus `GSSProvider` and `NTLMAuthenticationProviderBase`.

## Risks and Test Signals
Buffer descriptor offsets are trusted; invalid offsets become lower-level read exceptions. `ReadAnsiStringBufferPointer()` uses `ASCIIEncoding.Default`, which can be platform-sensitive. Tests should cover malformed lengths, zero-length buffers, all three NTLM message types, and v1/v2 response classification edge cases.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/Authentication/NTLM/Helpers/AuthenticationMessageUtils.cs -->
