# File Research: sources/os/plan9/plan9/sys/src/cmd/sam/sam.h

Defines the host `sam` core data model, constants, prototypes, and globals.

Key types:
- `Posn`, `Mod`, `Range`, `Rangeset`, `Address`, and `String` model positions, selections, and rune strings.
- `List` is a generic list union used for pointers, positions, strings, and files.
- `Block`, `Disk`, and `Buffer` model temp-file-backed text storage.
- `File` embeds `Buffer` and adds undo buffers, name/stat data, dirty state, dot/mark ranges, terminal rasp, protocol tag, and undo snapshots.

Key constants:
- `BLOCKSIZE`, `NDISC`, `NBUFFILES`, `NSUBEXP`, `INFINITY`, `STRSIZE`, buffer sizes, and log operation markers.

API surface:
- Declares disk, buffer, file, rasp, utility, regex, command, shell, string, protocol, terminal, and system functions.
- Declares major global state: `seq`, `disk`, `file`, `tempfile`, `cmd`, `curfile`, `addr`, `sel`, `snarfbuf`, `plan9buf`, `lastpat`, `lastregexp`, `downloaded`, `termlocked`, and `outbuffered`.

Behavior notes:
- Includes `mesg.h` at the end because protocol definitions depend on common constants and are used by `outT*` prototypes.
