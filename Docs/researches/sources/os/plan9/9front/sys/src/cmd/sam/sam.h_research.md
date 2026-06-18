# File Research: sources/os/plan9/9front/sys/src/cmd/sam/sam.h

`sam.h` is the shared host-side sam header. It defines core constants, types, structs, function prototypes, globals, and includes `mesg.h`.

Core types include `Posn`, `Mod`, `Range`, `Rangeset`, `Address`, `String`, `List`, `Block`, `Disk`, `Buffer`, and `File`. `File` embeds `Buffer` and adds undo buffers, filename, file identity, dirty/unread state, sequence numbers, dot/mark state, terminal rasp, protocol tag, close/delete flags, and previous state for rollback.

It declares temp-disk APIs, buffer APIs, file/undo APIs, rasp APIs, command/parse/search APIs, terminal protocol output APIs, Plan 9 system wrappers, string helpers, file-list/menu helpers, and utility routines.

Important constants include `BLOCKSIZE`, `NSUBEXP`, `STRSIZE`, `Maxblock`, buffer sizes, and file state markers. It also defines rune allocation/move macros and exposes global editor state such as `seq`, `disk`, `curfile`, `cmd`, `addr`, `snarfbuf`, `file`, `downloaded`, and protocol buffers.
