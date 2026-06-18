<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/git-annex/doc/special_remotes/p2p/git-annex-p2p-iroh -->
# sources/sync-backup/git-annex/doc/special_remotes/p2p/git-annex-p2p-iroh

Purpose: P2P transport adapter that lets git-annex use Iroh's `dumbpipe` for peer-to-peer connections.

Important behavior: resolves the repository git dir, stores a secret at `$git_dir/annex/creds/iroh-secret`, and exports it as `IROH_SECRET` for dumbpipe. In `address` mode it creates the credential directory, generates 32 random bytes with `gpg --gen-random 16 32` under `umask 077` if needed, then runs `dumbpipe generate-ticket`. In connect mode, if no socket file is supplied, it runs `dumbpipe connect <peeraddress>`. In listen mode, it loads the secret and runs `dumbpipe listen-unix --socket-path=<socketfile>`.

State and persistence: persists the Iroh secret inside `.git/annex/creds` so the node identity/ticket remains stable. Runtime state is delegated to dumbpipe sockets and network sessions.

Dependencies and integration points: `git rev-parse --git-dir`, `gpg`, `dumbpipe` version 0.33 or newer with `generate-ticket`, and git-annex's P2P transport program interface.

Risks: the secret file redirection is unquoted, so unusual repository paths could break. Secret generation depends on GPG availability. The script suppresses stderr only while generating the ticket to avoid secret display but otherwise delegates security to dumbpipe.

Test signals: address generation creates a 0600-style secret, repeated address calls reuse it, connect mode relays stdio, listen mode binds the provided Unix socket, and missing dumbpipe/GPG errors are visible.
<!-- END_FILE_RESEARCH: sources/sync-backup/git-annex/doc/special_remotes/p2p/git-annex-p2p-iroh -->
