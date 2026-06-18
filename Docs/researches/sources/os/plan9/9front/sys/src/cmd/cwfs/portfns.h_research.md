# File Research: sources/os/plan9/9front/sys/src/cmd/cwfs/portfns.h

Purpose: Function prototype header for cwfs.

Coverage:
- Filesystem operations: attach/clone/create/open/read/write/walk/remove/stat/session helpers.
- Device dispatch and implementations: cw, wren, worm/juke, fake worm, mcat/mlev/mirror/part/swap devices.
- Buffer/cache operations: `getbuf`, `putbuf`, allocation/freeing, tags, indirect addressing, readahead.
- Server/concurrency operations: queues, message buffers, `serve`, `srvchan`, `newproc`, network init/start.
- User/group operations: uid parsing, formatting, group checks, user commands.
- Console/command operations: command install/exec, config printing, checks.
- SCSI and time operations: SCSI command wrappers, `toytime`, `nextime`, formatting.
- Recovery/ream/dump/sync operations.

Notable details:
- The header exposes cross-file contracts for nearly every `.c` in `cwfs`.
- Some declared juke helper names such as `jukeread`/`jukewrite`/`jukesize` are not the primary implementations in `juke.c`, which provides `wormread`/`wormwrite`/`wormsize` for worm side devices.
