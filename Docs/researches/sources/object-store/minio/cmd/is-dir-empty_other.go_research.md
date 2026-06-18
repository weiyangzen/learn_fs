# sources/object-store/minio/cmd/is-dir-empty_other.go

## Purpose

`is-dir-empty_other.go` provides the non-Linux implementation of `isDirEmpty`, using a portable directory read instead of Linux link-count optimization.

## Important APIs, Types, And Control Flow

The build tag selects all non-Linux platforms. `isDirEmpty(dirname string, _ bool)` ignores the legacy flag, calls `readDirN(dirname, 1)`, returns false on error, and returns true only when no entry is read. This directly checks whether at least one object/prefix exists in the directory.

## State, Dependencies, Integration, Risks, And Tests

There is no persistent state. The only dependency is package-local `readDirN`. Integration is the same as the Linux implementation: callers can use a single `isDirEmpty` API across platforms. Risks are ordinary directory-read races with concurrent modifications, cost compared with Linux `stat`, and behavior differences if `readDirN` filters entries. There are no direct tests in this subset; correctness is generally covered by platform builds and higher-level filesystem/object layout tests.
