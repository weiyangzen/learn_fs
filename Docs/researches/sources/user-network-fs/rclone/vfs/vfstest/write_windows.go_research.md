# sources/user-network-fs/rclone/vfs/vfstest/write_windows.go

## Purpose
Provides Windows-specific fd duplication support and skips the write double-close behavioral test.

## APIs, Flow, And State
`TestWriteFileDoubleClose` reports an unsupported skip. `writeTestDup` uses `windows.DuplicateHandle` on the current process to duplicate a handle with the same access rights.

## Dependencies And Integration
Selected on Windows and used by shared write tests such as `TestWriteFileDup` when applicable.

## Risks And Test Signals
The duplicate helper can still support mmap-like tests, but the direct double-close write test is skipped. Windows handle semantics and WinFSP behavior remain the key platform risk.
