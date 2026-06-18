# File Research: sources/os/plan9/plan9/sys/src/cmd/unix/9pfreebsd/mount_9fs/mount_9fs.c

Read fully: 1045 lines, 25118 bytes. SHA-256 prefix: `42739908fca7f8c6`.

This is a FreeBSD mount helper adapted from `mount_nfs.c` for a 9FS/u9fs filesystem. Large portions of NFS option handling and Kerberos scaffolding remain, but the active path builds `struct u9fs_args` for a 9P-style mount.

Important behavior:
- Parses many NFS-style options, plus `-u user[@authhost]` to set Plan 9 username and auth address.
- `getnfsargs()` accepts `host:path` or `path@host`, resolves the server, sets port `U9FS_PORT`, fills socket/mount args, prompts for a Plan 9 password, derives a DES key, and loads `/etc/9uid.conf`.
- `load_9uid()` builds UID-to-Plan 9-name mappings.
- `passtokey()` converts a password into a Plan 9 DES key using `encrypt9()`.
- `load_9key()` prompts with `getpass()`.
- `gethostaddr()` resolves numeric or named hosts.
- `xdr_dir()` and `xdr_fh()` are retained NFS mount RPC helpers, mostly disabled in the active code.

Risk notes: the command still reports NFS usage text, has disabled NFS mount-protocol sections, and contains an `XXX` in Kerberos encryption code.
