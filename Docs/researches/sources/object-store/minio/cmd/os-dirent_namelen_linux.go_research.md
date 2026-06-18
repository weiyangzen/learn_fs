# sources/object-store/minio/cmd/os-dirent_namelen_linux.go

## Purpose
This Linux-specific helper computes the length of a directory-entry name from `syscall.Dirent` by scanning the fixed name buffer up to the record length for a terminating NUL byte.

## Important APIs, Types, and Functions
- Build tags: `linux && !appengine`.
- `direntNamlen(dirent *syscall.Dirent) (uint64, error)` calculates the usable name-buffer limit from `Reclen`, `unsafe.Offsetof(syscall.Dirent{}.Name)`, and the static name buffer size, then uses `bytes.IndexByte` to find the first zero byte.

## Control Flow
The function computes the fixed header size, creates a byte-array view over `dirent.Name` using `unsafe`, caps the scan limit to the smaller of `Reclen - fixedHdr` and the name-buffer length, scans for a zero terminator, returns an error if none is found, and otherwise returns the index as the name length.

## State and Persistence Behavior
The function is pure from the caller's perspective. It reads memory from the supplied `Dirent` and returns either a length or an error. It does not persist or mutate data.

## Dependencies and Integration Points
It depends on `bytes`, `fmt`, `syscall`, and `unsafe`. It is the Linux counterpart to BSD/Darwin `Namlen` field access, allowing directory traversal code to use `direntNamlen` portably.

## Risks and Edge Cases
- The function uses `unsafe.Pointer` into `dirent.Name`; callers must pass a valid `Dirent`.
- `dirent.Reclen - fixedHdr` is unsigned arithmetic. If a malformed record has `Reclen < fixedHdr`, the value can underflow before being capped to name-buffer length.
- Missing NUL terminators return an explicit error to avoid long-name bugs.
- Build tags exclude App Engine and non-Linux platforms.

## Test Signals
No direct tests are present. Indirect signals are Linux builds and any filesystem directory-reading tests that encounter normal and long names.
