# `sources/user-network-fs/go-fuse/fuse/print_linux.go`

## Purpose
Linux-specific debug string formatting for open/statx/capability flags.

## Important APIs, Types, And Functions
Registers Linux-only open and init flags, defines `Statx.string`, and `StatxIn.string`.

## Control Flow
Registers Linux-only open and init flags, defines `Statx.string`, and `StatxIn.string`.

## State And Persistence
Global printer tables are mutated at init. Dependencies include `runtime`, `syscall`, and `x/sys/unix`. Risks include architecture-specific flag aliases like `O_LARGEFILE`/`O_DIRECT` and keeping statx field names current.

## Dependencies And Integration Points
Dependencies and integration are captured by the package imports and neighboring files in this subset.

## Risks And Edge Cases
Global printer tables are mutated at init. Dependencies include `runtime`, `syscall`, and `x/sys/unix`. Risks include architecture-specific flag aliases like `O_LARGEFILE`/`O_DIRECT` and keeping statx field names current.

## Test Signals
Global printer tables are mutated at init. Dependencies include `runtime`, `syscall`, and `x/sys/unix`. Risks include architecture-specific flag aliases like `O_LARGEFILE`/`O_DIRECT` and keeping statx field names current.
