<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/git-annex/doc/special_remotes/p2p/git-annex-p2p-unix-sockets -->
# sources/sync-backup/git-annex/doc/special_remotes/p2p/git-annex-p2p-unix-sockets

Purpose: example P2P transport program that simulates a multi-node network by mapping peer addresses to Unix socket files under `/tmp`.

Control flow: in `address` mode, prints the current Unix timestamp as a mock local address. In connect mode with only a peer address, runs `socat - UNIX-CONNECT:/tmp/<peeraddress>` to relay stdin/stdout. In listen mode with a socket file, symlinks the real socket path to `/tmp/<myaddress>`.

State and persistence: creates or overwrites symlinks in `/tmp`. Addresses are timestamp-based and not stable across invocations.

Dependencies and integration points: POSIX shell, `date`, `realpath`, `ln`, `socat`, and the git-annex P2P transport interface.

Risks: predictable `/tmp` names and symlink replacement are insecure for real deployments; the file is explicitly a demo. Address collisions are possible for invocations in the same second. No cleanup of `/tmp` symlinks is performed.

Test signals: run address/listen/connect flows locally, verify data relays over the socket, test repeated address generation and stale symlink behavior.
<!-- END_FILE_RESEARCH: sources/sync-backup/git-annex/doc/special_remotes/p2p/git-annex-p2p-unix-sockets -->
