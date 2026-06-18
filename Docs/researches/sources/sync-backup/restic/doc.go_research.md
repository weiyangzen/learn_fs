# sources/sync-backup/restic/doc.go

## Purpose

This package documentation file describes the intended source layout of restic. It declares package `restic` and explains that the repository is primarily a command-line program rather than an importable library.

## Important APIs, Types, and Functions

There are no runtime APIs or functions. The file contains package-level Go documentation for `package restic`.

## Control Flow

There is no executable control flow.

## State and Persistence Behavior

There is no state or persistence behavior.

## Dependencies and Integration Points

The file has no imports. Its integration point is Go documentation tooling: `go doc` and package documentation generated from comments. It establishes architectural context for `cmd/` as the main binary package and `internal/` as the location of almost all library-form implementation.

## Risks and Edge Cases

The key maintenance risk is documentation drift if restic's architecture changes or if internal packages become supported library APIs. The comment explicitly says the non-library decision may be revisited later.

## Test Signals

There are no direct tests. Documentation consistency is indirectly checked by normal Go package parsing and documentation generation.
