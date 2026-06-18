<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary.Win32/Security/Structures/SecBufferDesc.cs -->
# sources/user-network-fs/smblibrary/SMBLibrary.Win32/Security/Structures/SecBufferDesc.cs

## Purpose
`SecBufferDesc.cs` defines the SSPI `SecBufferDesc` wrapper used to pass one or more `SecBuffer` structures to secur32 APIs.

## Important APIs, Types, And Functions
`SecBufferDesc : IDisposable` has `SECBUFFER_VERSION`, `ulVersion`, `cBuffers`, and `pBuffers`. Constructors accept one `SecBuffer` or an array. `GetBufferBytes(int bufferIndex)` marshals a `SecBuffer` from the descriptor and returns its bytes. `Dispose` frees the descriptor array memory.

## Control Flow
The array constructor allocates unmanaged memory sized for all buffer structs and copies each `SecBuffer` struct into it. `GetBufferBytes` checks disposal, computes the indexed struct pointer, unmarshals it, and calls `SecBuffer.GetBufferBytes`. `Dispose` frees `pBuffers`.

## State And Persistence
It owns unmanaged memory for the descriptor's array of `SecBuffer` structs, not necessarily the pointed-to token buffers themselves. No persistent state is written.

## Dependencies And Integration Points
It depends on `SecBuffer` and marshaling. `SSPIHelper` uses it for `InitializeSecurityContext` and `AcceptSecurityContext` input/output buffers.

## Risks
It does not dispose the underlying `SecBuffer` instances; callers must free both descriptor and buffers. As a struct, copies can duplicate ownership of `pBuffers`. Bounds are not checked in `GetBufferBytes`, so invalid indexes can marshal arbitrary memory.

## Test Signals
No direct tests; behavior is covered only through SSPI calls.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary.Win32/Security/Structures/SecBufferDesc.cs -->
