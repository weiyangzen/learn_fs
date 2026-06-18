# `sources/user-network-fs/go-fuse/fuse/pathfs/readonlyfs.go`

## Purpose
Implements `NewReadonlyFileSystem`, a decorator that blocks mutating pathfs operations while allowing reads and metadata lookup.

## Important APIs, Types, And Functions
`readonlyFileSystem` forwards read-only methods (`GetAttr`, `Readlink`, `OpenDir`, read-only `Open`, xattr get/list, statfs) and returns `EROFS` for mutation paths.

## Control Flow
`readonlyFileSystem` forwards read-only methods (`GetAttr`, `Readlink`, `OpenDir`, read-only `Open`, xattr get/list, statfs) and returns `EROFS` for mutation paths.

## State And Persistence
State is just the wrapped filesystem. `Open` checks write flags and rejects writes before delegating. Risks include missing a mutating method or misclassifying flags. It integrates as a simple safety wrapper above any pathfs implementation.

## Dependencies And Integration Points
Dependencies and integration are captured by the package imports and neighboring files in this subset.

## Risks And Edge Cases
State is just the wrapped filesystem. `Open` checks write flags and rejects writes before delegating. Risks include missing a mutating method or misclassifying flags. It integrates as a simple safety wrapper above any pathfs implementation.

## Test Signals
State is just the wrapped filesystem. `Open` checks write flags and rejects writes before delegating. Risks include missing a mutating method or misclassifying flags. It integrates as a simple safety wrapper above any pathfs implementation.
