# sources/sync-backup/syncthing/lib/fs/basicfs_windows_test.go

## Purpose
Windows-only tests for root normalization, long-path support, 8.3 path handling, case-insensitive relative conversion, final path resolution, and read-only removal behavior.

## Important APIs, Types, and Functions
Tests target `newBasicFilesystem`, `resolveWin83`, `isMaybeWin83`, `rel`, `unrootedChecked`, `getFinalPathName`, and `Remove`.

## Control Flow
Table-driven tests assert expected `root` and `URI` for drive and UNC inputs. 8.3 tests create a long filename and verify short-name expansion or fallback truncation. Rel tests exercise mixed-case roots. Removal test sets a directory read-only attribute and confirms `BasicFilesystem.Remove` clears enough attributes to delete it.

## State and Persistence Behavior
Creates files/directories in temp roots and mutates Windows file attributes. Some tests query system paths such as `C:\Windows\System32`.

## Dependencies and Integration Points
Uses `syscall` Windows APIs, `TempName`, and shared `setup`.

## Risks
Tests depend on Windows filesystem behavior, short-name support, and permissions. Some final-path cases ignore missing paths to avoid environment-specific failures.

## Test Signals
Strong Windows regression coverage for path canonicalization, watcher root matching prerequisites, and deletion of read-only/custom-icon folders.
