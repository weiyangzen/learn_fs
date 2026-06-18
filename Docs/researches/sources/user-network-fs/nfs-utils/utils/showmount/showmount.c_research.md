## sources/user-network-fs/nfs-utils/utils/showmount/showmount.c

Purpose: Implements `showmount`, querying a remote mountd service for exports or active mount entries.

Important APIs/types/functions: `nfs_get_mount_client` creates a TCP or UDP RPC client using mount program aliases. `dump_cmp` sorts output. `main` handles `-a`, `-d`, `-e`, `--no-headers`, version fallback, RPC calls, and formatting.

Control flow: Options choose exactly one mode: host list default, all host:directory pairs, directories, or exports. It chooses localhost by default, creates an authenticated mount RPC client, tries mount protocol versions in order on version mismatch, calls `MOUNTPROC_EXPORT` or `MOUNTPROC_DUMP`, sorts dump entries, suppresses duplicates, and prints.

State and persistence: Stateless client. Reads no local persistent data beyond hostname and RPC database; remote mountd provides all data.

Dependencies and integration: Uses RPC mount protocol XDR types from `mount.h`, `nfsrpc.h` authentication helpers, and libtirpc/SunRPC.

Risks and test signals: Remote RPC failures exit directly, memory for `-a` strings is not freed before exit, and output depends on mountd v1/v2/v3 compatibility. Tests should mock mountd responses for exports, duplicates, version mismatch, no headers, invalid mode combinations, and unreachable hosts.
