# sources/user-network-fs/smblibrary/SMBLibrary.Adapters/NTFileSystemAdapter/IOExceptionHelper.cs
# sources/user-network-fs/smblibrary/SMBLibrary.Adapters/NTFileSystemAdapter/IOExceptionHelper.cs

Purpose: C# helper for extracting Windows error information from `IOException`. API surface is `GetWin32ErrorCode(IOException ex)` returning a `ushort` derived from the exception HResult, and `GetExceptionHResult(IOException ex)` exposing the raw HResult.

State and persistence: stateless static methods only. Dependencies are .NET `System.IO.IOException` and HResult conventions. Integration point is NT filesystem adapter error translation from .NET exceptions to SMB/Win32-style error codes. Risks include truncating or misinterpreting non-Win32 HResults, platform differences, and relying on exception internals. Test signal is absent in this file; callers need coverage for representative IO errors.
