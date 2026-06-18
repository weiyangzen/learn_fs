# sources/sync-backup/borg/docs/usage/version.rst.inc

Purpose: Documents `borg version`, which reports Borg client and server versions.

Important APIs/types/functions: CLI contract is `borg [common options] version [options]` with no command-specific options. The output is `client / server`, using simplified version formatting from `borg.version.format_version`.

Control flow: Runtime determines whether the repository is local or remote. Local repositories report the client as both client and server; remote repositories query the remote Borg server and display its version.

State and persistence: Read-only. It may initiate remote negotiation but does not alter repository state.

Dependencies and integration points: Integrates with remote repository protocol negotiation, `borg serve`, legacy server compatibility, and `borg --version` for more precise client-only version output.

Risks: Simplified version output may hide local package metadata. Remote connection errors should produce useful diagnostics.

Test signals: Cover local repo output, remote server version negotiation, old server compatibility, and contrast with `borg --version`.
