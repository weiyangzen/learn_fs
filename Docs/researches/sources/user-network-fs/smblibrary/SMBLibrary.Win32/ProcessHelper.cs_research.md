<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary.Win32/ProcessHelper.cs -->
# sources/user-network-fs/smblibrary/SMBLibrary.Win32/ProcessHelper.cs

## Purpose
`ProcessHelper.cs` provides process and operating-system bitness detection for Win32 interop code.

## Important APIs, Types, And Functions
The class P/Invokes `kernel32!IsWow64Process`. Public APIs are `IsWow64Process(Process process)`, `IsWow64Process()`, `Is64BitProcess`, and `Is64BitOperatingSystem`. Results for the current process are cached in nullable booleans.

## Control Flow
The process-specific method calls `IsWow64Process` only on OS versions expected to support it, returning false on failure or older systems. The parameterless method caches the current process result. `Is64BitProcess` caches `IntPtr.Size == 8`, and `Is64BitOperatingSystem` combines native 64-bit process or WOW64 process detection.

## State And Persistence
Only process-local cached booleans are stored. No persistent state is written.

## Dependencies And Integration Points
It depends on `System.Diagnostics.Process`, `Environment.OSVersion`, and kernel32. `NTDirectoryFileSystem.SetFileInformation` uses `Is64BitProcess` to choose file rename/link information structures.

## Risks
OS version checks can be affected by application manifest/version lie behavior. Failed `IsWow64Process` calls silently return false. Cache values do not adapt if called in unusual process emulation scenarios, though that is normally stable.

## Test Signals
No tests in this subset cover process bitness detection. Integration is indirect through Win32 set-information paths.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary.Win32/ProcessHelper.cs -->
