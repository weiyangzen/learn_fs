# sources/sync-backup/bup/lib/bup/cmd/server.py

## Purpose
`server.py` starts a bup protocol server on stdin/stdout, serving repository operations to clients over an existing transport such as SSH.

## APIs and Control Flow
`main(argv)` rejects arguments, logs a debug message, defines a `ServerRepo` subclass that checks the requested repo and initializes `LocalRepo` with a server reference, then wraps byte stdin/stdout in `Conn` and runs `protocol.Server.handle()`.

## State, Dependencies, Integration, Risks, Tests
Persistent effects depend on allowed protocol commands: reads, object writes, and ref updates can occur through the server. Dependencies include `protocol.Server`, `LocalRepo`, `git.check_repo_or_die`, and `helpers.Conn`. It integrates with remote repository clients and generic bup transport. Risks include broad protocol exposure compared with `on.py` restricted configs, transport EOF/error behavior, and repository path validation. Test signals include no-argument enforcement, byte-stream wrapping, server command handling through `Conn`, and `ServerRepo` repo validation.
