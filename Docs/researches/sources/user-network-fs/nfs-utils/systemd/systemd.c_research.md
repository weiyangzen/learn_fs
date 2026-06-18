# sources/user-network-fs/nfs-utils/systemd/systemd.c

Purpose: `systemd.c` provides helper functions shared by nfs-utils systemd generators.

Important APIs and control flow: `systemd_escape` implements systemd path-to-unit escaping: trim leading/trailing slash behavior, collapse slash runs to `-`, encode root as `-`, leave ASCII alnum, `:`, `.`, and `_`, and encode other bytes as `\xNN`. `systemd_len` computes allocation size, and `hexify` writes escape sequences. `systemd_in_initrd` checks `/etc/initrd-release`.

State, dependencies, and integration: It allocates returned unit names for callers to free and uses only libc/system calls. Generators for nfs-server, nfsroot, and rpc-pipefs depend on it.

Risks and test signals: `systemd_escape` does not check `malloc` before writing through `result`, and the allowed-character set must stay aligned with systemd. Tests should cover root, duplicate slashes, leading dots, spaces, non-ASCII bytes, colons, suffix appending, and malloc failure handling if injectable.
