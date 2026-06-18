<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/libcap/cap/fdlegacy.go -->
# sources/security-integrity/libcap/cap/fdlegacy.go

## Purpose
Legacy pre-Go-1.12 fallback for extracting an `os.File` descriptor.

## Important APIs, Types, And Functions
Defines `fd(file *os.File) uintptr` as `uintptr(file.Fd())` under build tag `!go1.12`.

## Control Flow
Returns the descriptor directly from the standard library.

## State And Persistence Behavior
No explicit state is changed, but direct `Fd()` can cause Go runtime polling/thread behavior changes on old toolchains.

## Dependencies And Integration Points
Used by `file.go` when building with old Go versions.

## Risks And Edge Cases
The file comment notes this path is suboptimal because it can lock a thread to syscalls.

## Test Signals
Signals are successful file capability operations on legacy Go toolchains.
<!-- END_FILE_RESEARCH: sources/security-integrity/libcap/cap/fdlegacy.go -->
