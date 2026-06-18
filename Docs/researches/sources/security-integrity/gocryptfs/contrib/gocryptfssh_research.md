# sources/security-integrity/gocryptfs/contrib/gocryptfssh

Purpose: This script integrates gocryptfs with SSH-style remote access, likely mounting encrypted storage over an SSH transport or exposing a helper command for remote encrypted home/work directories.

Important APIs and steps: It parses shell options, invokes `ssh`, `sshfs`, or gocryptfs-related commands, and coordinates mount paths.

Control flow and state: Runtime control flow validates arguments, establishes remote/local mounts, and exits on command failures. Persistent state can include active SSH/FUSE mounts.

Dependencies and integration points: Contrib-level integration with gocryptfs, SSH tooling, and FUSE mount helpers.

Risks and test signals: Risks include quoting of remote paths, credential prompts, stale mounts, and shell injection if paths are not quoted. Signals are successful mount/session setup and cleanup under paths with spaces or unusual characters.
