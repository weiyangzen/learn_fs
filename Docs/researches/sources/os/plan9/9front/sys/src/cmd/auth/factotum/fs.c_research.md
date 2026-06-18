# File Research: sources/os/plan9/9front/sys/src/cmd/auth/factotum/fs.c

Factotum main program and 9P file server exposing `/mnt/factotum`.

Key responsibilities:
- Parses factotum flags for server/user mode, debug, prompting, secstore use, mount point, service name, and bootstrap auth addresses.
- Initializes the keyring, protocol table, formatters, capability support, and optional NVRAM keys.
- Mounts/posts the factotum file server, normally as `/mnt/factotum`.
- Optionally imports keys from secstore.
- Exposes files `ctl`, `rpc`, `proto`, `log`, `confirm`, and `needkey`.
- Implements attach, walk, stat, open, read, write, flush, and fid cleanup for the virtual filesystem.
- Routes `rpc` operations to `rpc.c`, control writes to `ctlwrite`, and confirm/needkey/log reads to their queues.
- Lists keys via `ctl` reads and supported protocol names via `proto`.

Dependencies:
- Uses lib9p `Srv`, factotum protocol modules, `postsrerv`/mount semantics, NVRAM auth helpers, and secstore command execution.

Notable risks:
- `confirm`, `needkey`, and `log` are exclusive-use files.
- Each open file gets a fresh `Fsstate`; cleanup must close protocol state and free attrs.
