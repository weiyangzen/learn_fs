# File Research: sources/os/plan9/plan9/sys/src/9/port/qio.c

Implements Plan 9 kernel I/O queues and block-list utilities.

Block utilities:
- `freeblist`, `padblock`, `blocklen`, `blockalloclen`, `concatblock`, `pullupblock`, `pullupqueue`, `trimblock`, `copyblock`, `adjustblock`, `pullblock`, `packblock`.
- `bl2mem` and `mem2bl` convert between memory buffers and block chains.
- Maintains optional debug/stat counters for block transformations.

Queue model:
- `Queue` stores block chains, byte/accounting limits, state bits, read/write locks, rendezvous points, kick/bypass callbacks, and close error text.
- `qopen` creates a normal queue; `qbypass` creates a bypass queue.
- `qread`/`qbread` block until data or close; `qwrite`/`qbwrite` queue data with flow control.
- Interrupt-safe APIs include `qproduce`, `qconsume`, `qpass`, `qpassnolim`, and `qiwrite`.
- `qget`, `qdiscard`, `qcopy`, `qremove`, `qputback`, and `qaddlist` operate on queued blocks.
- `qclose`, `qhangup`, `qreopen`, `qflush`, `qfree` manage lifecycle.
- `qlen`, `qwindow`, `qcanread`, `qfull`, `qisclosed`, `qsetlimit`, and `qnoblock` expose queue state.

Important behavior:
- Message queues preserve message boundaries; byte queues may split and put back partial blocks.
- Flow control wakes writers when queue length falls below thresholds.
- `qbwrite` queues data before sleeping for flow control so notes do not interrupt already-committed writes.
- `qiwrite` is designed for printing from high priority or non-process contexts and drops data above a hard print-buffer threshold.
- `qclose` discards queued blocks; `qhangup` marks closed but preserves queued data.

Role:
- Shared substrate for devices, network input queues, pipes, consoles, and kernel print queues.
