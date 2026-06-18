# sources/object-store/minio-mc/cmd/admin-top-locks.go

## Purpose

`admin-top-locks.go` defines the legacy `mc admin top locks` command and redirects users to `mc support top locks`.

## Important APIs, Types, and Functions

`topLocksFlag` declares `--stale` and hidden `--count`. `adminTopLocksCmd` is wired to `mainAdminTopLocks`, which emits the deprecation message.

## Control Flow

The CLI parses the command and flags, then the handler immediately calls `deprecatedError("mc support top locks")`.

## State and Persistence Behavior

No state is read or written by this file.

## Dependencies and Integration Points

It is registered by `admin-top.go` and shares global flags plus usage-error behavior.

## Risks and Edge Cases

Unlike `admin top api`, this command is not marked hidden in the command declaration in this file, so visibility depends on parent grouping and current CLI help behavior. The retained hidden `count` flag has no effect after deprecation.

## Test Signals

Tests should check command visibility expectations, flag parsing, and deprecation target.
