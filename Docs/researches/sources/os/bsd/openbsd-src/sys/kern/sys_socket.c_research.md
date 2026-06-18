# File Research: sources/os/bsd/openbsd-src/sys/kern/sys_socket.c

Defines file operations for sockets represented as kernel files.

Core behavior:
- `socketops` maps file operations to `soo_read`, `soo_write`, `soo_ioctl`, `soo_kqfilter`, `soo_stat`, and `soo_close`.
- `soo_read()` calls `soreceive()` and translates `FNONBLOCK` to `MSG_DONTWAIT`.
- `soo_write()` calls `sosend()` and likewise honors nonblocking mode.
- `soo_close()` calls `soclose()` with `MSG_DONTWAIT` when the file is nonblocking, then clears `f_data`.

Ioctls:
- `FIOASYNC` toggles async flags on both receive and send socket buffers while holding their mutexes.
- `FIONREAD` returns receive-buffer data byte count.
- owner and process-group ioctls use `sigio_setown()` and `sigio_getown()`.
- `SIOCATMARK` reports receive-at-mark state.
- interface ioctls are delegated to `ifioctl()`, routing ioctls return `EOPNOTSUPP`, and other protocol controls go to `pru_control()`.

Stat behavior:
- `soo_stat()` reports `S_IFSOCK`.
- Read permission bits are set if receive is still possible or data remains buffered.
- Write permission bits are set if send has not been shut down.
- uid/gid come from socket effective credentials, and protocol-specific status comes from `pru_sense()`.

Filesystem/storage relevance:
- Not filesystem code, but important for VFS file abstraction: sockets are non-vnode files with read/write/ioctl/stat/close behavior exposed through the same descriptor table as regular files.
