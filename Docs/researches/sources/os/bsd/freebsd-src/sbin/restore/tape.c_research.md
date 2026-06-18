# File Research: sources/os/bsd/freebsd-src/sbin/restore/tape.c

Purpose: tape/input I/O core for `restore`, including dump header validation, volume changes, block buffering, file extraction, extended attributes, and byte swapping.

Key functions:
- `setinput()` configures local file, stdin pipe, pipe command, or optional remote tape input and drops privileges to the real UID.
- `setup()` opens volume 1, detects block size, validates dump headers, initializes `usedinomap` and `dumpmap`, and sets dump metadata.
- `getvol()` prompts/opens later volumes, validates dump dates and volume numbers, and resumes active file extraction when needed.
- `extractfile()` creates filesystem objects for regular files, symlinks, directories, FIFOs, devices, sockets, and applies metadata.
- `set_extattr()` restores UFS extended attributes and has ACL-specific fallback paths.
- `getfile()` walks dump block maps, dispatching data, extattr, and sparse-hole callbacks.
- `readtape()`, `gethead()`, `findinode()`, and `findtapeblksize()` manage buffered reads, errors, EOT, resynchronization, and header normalization.
- `swabst()` and helpers support opposite-endian or old-format dumps.

Integration: drives `curfile` and `spcl`, feeding all higher-level restore logic. It calls into directory extraction, file creation, maps, volume checkpointing, and external remote tape functions when compiled with `RRESTORE`.

Risk notes: this is the most error-sensitive module. It uses `setjmp`/`longjmp` for volume continuation, many globals for tape position, and manual buffer management. Corrupt media paths rely on `Dflag`/`yflag` recovery choices and checksum/header validation.
