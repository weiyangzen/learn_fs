# File Research: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/kern/qio.c

This file implements Plan 9-style block queues used by drawterm devices, pipes, network paths, and stream-like kernel components.

Key behavior:
- Block helpers include `freeblist`, `padblock`, `blocklen`, `blockalloclen`, `concatblock`, `pullupblock`, `pullupqueue`, `trimblock`, `copyblock`, `adjustblock`, `pullblock`, `packblock`, `bl2mem`, and `mem2bl`.
- Queue producers use `qpass`, `qpassnolim`, `qproduce`, `qbwrite`, `qwrite`, and interrupt-level `qiwrite`.
- Queue consumers use `qget`, `qconsume`, `qdiscard`, `qcopy`, `qbread`, and `qread`.
- Lifecycle/control functions include `qopen`, `qbypass`, `qfree`, `qclose`, `qhangup`, `qreopen`, `qflush`, `qsetlimit`, `qnoblock`, `qlen`, `qwindow`, `qcanread`, `qfull`, `qstate`, and `qisclosed`.

Important details:
- `Queue` tracks allocated bytes (`len`), payload bytes (`dlen`), limit, state flags, EOF count, optional kick callback, optional bypass callback, reader/writer locks, rendezvous points, and an error string.
- Flow control is based on `limit`; writers set `Qflow` and sleep on `wr`, readers wake writers once the queue drains.
- `Qmsg` preserves message boundaries; non-message queues may split/coalesce blocks.
- `qclose` discards buffered blocks and marks `Ehungup`; `qhangup` marks closed but leaves queued blocks readable.
- `Maxatomic`/`qiomaxatomic` limit atomic write chunking to 64 KiB.
