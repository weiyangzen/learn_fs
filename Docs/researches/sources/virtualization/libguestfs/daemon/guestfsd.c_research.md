# File Research: sources/virtualization/libguestfs/daemon/guestfsd.c

Daemon entry point and transport setup.

Important behavior:
- Parses daemon flags for channel path, listen mode, network enablement, standalone root mode, test mode, and verbosity.
- Initializes OCaml stubs with `caml_startup`.
- Sets controlled environment: `PATH`, `SHELL`, `LC_ALL=C`, `TERM=dumb`, and default umask.
- Opens virtio-serial channel by default, supports `fd:<n>`, or listens on a Unix socket.
- Sends `GUESTFS_LAUNCH_FLAG` to signal readiness, then enters `main_loop`.
- Provides `shell_quote` and `sysroot_shell_quote` utilities used by shell-pipeline wrappers.

Filesystem relevance: establishes the appliance daemon process, sysroot mode, and protocol channel that all filesystem operations use.
