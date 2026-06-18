# sources/sync-backup/rsync/rsync-ssl

Purpose: Bash wrapper that secures daemon-style rsync connections using `openssl`, `gnutls-cli`, or `stunnel` by acting as rsync's `--rsh` helper.

Important APIs, types, and functions: `rsync_ssl_run()` validates daemon-style arguments and execs `rsync --rsh="$0 --HELPER"`. `rsync_ssl_helper()` selects and configures TLS backend, parses rsync helper args, derives host/port/cert/key/CA options from environment, and execs the chosen client. `path_search()` locates helper binaries on `PATH`.

Control flow: User mode handles `--help`, `--type=...`, and ordinary rsync args. Helper mode expects `HOSTNAME rsync --server --daemon .`, ignores optional `-l USER`, chooses backend, builds verification options, defaults port to `RSYNC_PORT` or `RSYNC_SSL_PORT` or 874, then replaces the process with the TLS command connected to host:port.

State and persistence behavior: No files are persisted except stunnel's inherited here-doc config stream. Environment variables (`RSYNC_SSL_TYPE`, backend paths, cert/key/CA, ports) control behavior and are exported for recursive helper use.

Dependencies and integration points: Depends on bash, rsync, and one TLS backend. Used by `prepare-source` and users wanting daemon TLS without native rsync TLS support.

Risks and test signals: Risks include shell word splitting in exec command construction, weaker verification with stunnel defaults, backend option divergence, and hostname/port parsing limitations. Tests should run openssl/gnutls/stunnel modes, unset/empty/custom CA behavior, helper argument validation, and daemon URL rejection for non-daemon args.
