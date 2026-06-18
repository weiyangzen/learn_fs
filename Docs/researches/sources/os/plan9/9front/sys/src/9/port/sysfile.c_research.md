# File Research: sources/os/plan9/9front/sys/src/9/port/sysfile.c

Plan 9 file, descriptor, namespace, directory, mount, and stat syscall implementation.

Key responsibilities:
- Manages file descriptor allocation, growth, duplication, close-on-exec flags, and descriptor-to-channel lookup.
- Implements `pipe`, `dup`, `open`, `create`, `close`, `read`, `pread`, `write`, `pwrite`, `seek`, and old seek compatibility.
- Implements directory reads across union mounts and rewrites directory entries at mount points to match mounted channels.
- Uses `dirrock` to store directory entries that overflow after mount rewriting.
- Validates stat buffers and names for `stat`, `fstat`, `wstat`, and `fwstat`.
- Implements `chdir`, `bind`, `mount`, old `mount`, `unmount`, and namespace mount semantics.
- Prevents removal or renaming of mount points to avoid ambiguity.
- Implements legacy fixed-size stat packing for old binaries.

Dependencies:
- Uses channel/name resolution (`namec`, `walk`, `devtab`, `cmount`, `cunmount`, `findmount`), process file groups, and mount-head locks.
- Relies on Plan 9 Dir/stat wire-format helpers and error strings.

Notable behavior:
- File descriptor table growth is capped; exceeding descriptor hundreds can print a warning.
- Directory read offsets distinguish `c->devoffset` from logical `c->offset` because mount rewriting can change returned byte counts.
- `write()` advances the channel offset before calling the device and rolls back on error or short write.
- `bindmount()` closes the mounted fd after successful mount.
