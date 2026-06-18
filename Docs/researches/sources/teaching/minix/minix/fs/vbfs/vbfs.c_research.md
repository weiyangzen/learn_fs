# File Research: sources/teaching/minix/minix/fs/vbfs/vbfs.c

VBFS is the MINIX VirtualBox shared folder filesystem server. The file is intentionally thin: it configures and connects the SFFS layer to the VirtualBox shared-folder backend.

Key responsibilities:
- Defines the stack: `VBFS -> libsffs -> libvboxfs -> libsys/vbox -> VBOX driver -> VirtualBox host`.
- Parses `-o` mount/service options using `optset`:
  - `share`
  - `prefix`
  - `uid`
  - `gid`
  - `fmask`
  - `dmask`
- Sets defaults for ownership, masks, prefix, and case sensitivity.
- Requires a non-empty share name.
- Initializes `libvboxfs` with the share name, receives the SFFS operation table, case-sensitivity flag, and read-only flag.
- Initializes SFFS with server name `"VBFS"` and the resulting parameters.
- Registers SEF fresh-start initialization and delegates signal handling to `sffs_signal`.
- Runs `sffs_loop()` as the server loop and calls `vboxfs_cleanup()` after the loop exits.

Important interactions:
- `vboxfs_init` is responsible for host/share discovery and backend operations.
- `sffs_init` and `sffs_loop` provide the filesystem protocol implementation.
- `env_setargs` makes command-line options available as `env_argc/env_argv`.

Failure behavior:
- Missing share returns `EINVAL`.
- Unknown host share reports `ENOENT`.
- On SFFS init failure after VBOXFS init, the code cleans up `libvboxfs`.
