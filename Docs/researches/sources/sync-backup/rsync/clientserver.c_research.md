# sources/sync-backup/rsync/clientserver.c

## Purpose
Implements rsync daemon socket setup and the client side of the rsyncd in-band protocol. It negotiates the `@RSYNCD` greeting, selects/list modules, performs daemon authentication, applies module policy, prepares chroot/uid/gid/security state, runs configured transfer hooks, and hands an accepted module request into the normal sender/receiver server path.

## Important APIs, Types, and Functions
`start_socket_client()` opens a wrapped TCP connection and then calls `start_inband_exchange()` before `client_run()`. `exchange_protocols()` emits and parses daemon greetings, subprotocols, MOTD, and authentication digest lists. `start_inband_exchange()` sends the module name, handles `AUTHREQD`, `OK`, `EXIT`, `@ERROR`, early input, and daemon argument transport. `start_daemon()` is the accepted-connection entrypoint. `rsync_module()` is the main per-module policy and transfer setup routine. `daemon_main()`, `become_daemon()`, and `create_pid_file()` implement inetd/standalone daemon startup. `namecvt_call()` talks to a configured name-converter helper.

## Control Flow
Client flow validates that the remote path starts with a module, extracts optional `user@host`, connects, negotiates daemon protocol, sends module/options, and then enters `client_run()`. Server flow loads daemon config before logging, optionally reads PROXY protocol, pre-resolves DNS when ACLs may need it, applies daemon-level chroot/uid/gid, negotiates protocol, reads optional early input, lists modules or resolves a module name, then enters `rsync_module()`. Module flow checks access/auth, claims max-connection lock slots, resolves uid/gid/group policy, normalizes/chroots into the module path, loads daemon filters, starts early/pre/post/name-converter exec hooks, drops privileges, parses client options, starts multiplexing as needed, and calls `start_server()`.

## State and Persistence Behavior
The file mutates global transfer/daemon state such as `auth_user`, `read_only`, `module_id`, `module_dir`, `module_dirlen`, `full_module_path`, `early_input`, `namecvt_pid`, `daemon_chmod_modes`, `am_daemon`, `am_chrooted`, `am_root`, `sanitize_paths`, `munge_symlinks`, `use_secure_symlinks`, `numeric_ids`, `tmpdir`, and logging flags. Persistent process effects include pid-file creation and locking, max-connection lock ranges, environment variables for hooks, chroot, setuid/setgid/setgroups, and long-lived helper pipes for name conversion.

## Dependencies and Integration Points
Depends on daemon parameter accessors (`lp_*`), auth helpers, socket helpers, logging, filter parsing, path normalization, secure syscall wrappers, option parsing, protocol setup, multiplexed IO, process helpers, and cleanup/error handling. It integrates with `compat.c` via daemon greeting/subprotocol negotiation and with `exclude.c` via daemon filter construction and `set_filter_dir()`.

## Risks and Test Signals
High-risk areas are daemon path confinement, `/./` chroot split handling, daemon-chroot versus module-chroot symlink defenses, reverse-DNS timing for hostname ACLs, pid-file race protection, hook pipe lifecycle, early-input framing, privilege drop order, max-connection locks, and compatibility with old daemon protocols. Test signals include successful module listing, auth-required and auth-free module access, denied/unknown module errors, chrooted and non-chrooted transfers, `use chroot = no` symlink-race coverage, max-connection exhaustion, pid-file locking, hook failure propagation, and protocol downgrade behavior.
