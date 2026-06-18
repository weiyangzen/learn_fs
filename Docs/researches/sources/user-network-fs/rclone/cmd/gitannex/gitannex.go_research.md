<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/cmd/gitannex/gitannex.go -->
# sources/user-network-fs/rclone/cmd/gitannex/gitannex.go

## Purpose

`gitannex.go` implements `rclone gitannex`, an external special remote protocol server allowing git-annex to store, retrieve, check, and remove annex keys through rclone remotes.

## Important APIs, Types, and Functions

`maybeTransformArgs` inserts the `gitannex` subcommand when invoked through the `git-annex-remote-rclone-builtin` symlink. `messageParser` parses line protocol commands with space-delimited leading parameters and a final parameter that may contain spaces. `server` holds reader/writer, verbosity, negotiated extension booleans, and cached config. Handler methods implement `run`, `handleInitRemote`, `queryConfigs`, `handlePrepare`, `handleListConfigs`, `handleTransfer`, `handleCheckPresent`, `queryDirhash`, `handleRemove`, and `handleExtensions`. The Cobra command wires stdin/stdout to a server.

## Control Flow

The server sends `VERSION 1`, then loops over git-annex messages. It negotiates config lazily, validates remotes/layouts on init, builds per-key Fs strings by layout, uses `operations.CopyFile` for STORE/RETRIEVE, `NewObject` for presence checks, and `operations.DeleteFile` for removal.

## State and Persistence Behavior

In-process state is config and extension negotiation. Persistent remote effects are storing and deleting key objects. Local effects include retrieved files. It writes protocol messages to stdout and optional transcripts to stderr.

## Dependencies and Integration Points

It integrates git-annex's external special remote protocol, rclone Fs cache, `operations`, embedded help, layout/config helpers, and Cobra aliasing.

## Risks and Test Signals

Risks include protocol desynchronization, panics on write errors, config caching across sessions, no ASYNC implementation despite tracking extension flags, layout path mistakes, partial transfer errors, missing queryConfigs in some handlers, and stdout pollution. Tests should cover parser edges, protocol handlers, remote validation, every layout, store/retrieve/remove/check flows, symlink invocation, and real git-annex e2e behavior.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/cmd/gitannex/gitannex.go -->
