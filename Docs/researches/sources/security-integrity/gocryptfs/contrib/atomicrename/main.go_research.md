# sources/security-integrity/gocryptfs/contrib/atomicrename/main.go

Purpose: This contrib tool stress-tests atomic rename behavior, useful for filesystems and FUSE implementations.

Important APIs and functions: The program creates/writes files, repeatedly renames between paths, and likely checks visible content or existence invariants using Go `os` operations.

Control flow and state: It runs a loop over temporary or user-supplied paths, mutating filesystem namespace state through rename operations. State is on-disk test files.

Dependencies and integration points: Used manually against gocryptfs mounts or backing filesystems to observe rename atomicity and crash/visibility behavior.

Risks and test signals: As a contrib diagnostic, it may be destructive in the target directory if used carelessly. Signals are absence of inconsistent intermediate states, failed renames, or unexpected file contents.
