<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary.Win32/Security/Structures/SecBuffer.cs -->
# sources/user-network-fs/smblibrary/SMBLibrary.Win32/Security/Structures/SecBuffer.cs

## Purpose
`SecBuffer.cs` defines managed wrappers for SSPI `SecBuffer` structures and unmanaged token/data buffers.

## Important APIs, Types, And Functions
It defines `SecBufferType` values `SECBUFFER_EMPTY`, `SECBUFFER_DATA`, and `SECBUFFER_TOKEN`, plus `SecBuffer : IDisposable` fields `cbBuffer`, `BufferType`, and `pvBuffer`. Constructors allocate by size or copy byte arrays. `Dispose` frees unmanaged memory and `GetBufferBytes` copies bytes back to managed arrays.

## Control Flow
Constructors allocate `Marshal.AllocHGlobal` and optionally `Marshal.Copy` input bytes. `GetBufferBytes` returns null for zero-length buffers or copies `cbBuffer` bytes from `pvBuffer`. `Dispose` frees `pvBuffer` if non-zero.

## State And Persistence
Each `SecBuffer` owns unmanaged memory until disposed. No persistent state is written.

## Dependencies And Integration Points
It depends on `System.Runtime.InteropServices` and is used by `SSPIHelper` NTLM/Kerberos context calls through `SecBufferDesc`.

## Risks
As a struct with unmanaged ownership, copying `SecBuffer` values can duplicate the pointer and make double-free or leak patterns easy. Constructors do not guard against null byte arrays. Callers must dispose explicitly even on exceptions.

## Test Signals
No direct tests. It is indirectly exercised by SSPI authentication paths when run on Windows.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary.Win32/Security/Structures/SecBuffer.cs -->
