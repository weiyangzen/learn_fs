# File Research: sources/os/plan9/9front/sys/src/cmd/spin/mesg.c

`mesg.c` implements Spin’s simulation-time channel and message behavior. It creates queue instances, handles asynchronous and rendezvous send/receive operations, performs message-field type checks, prints send/receive traces, dumps queue contents, and validates channel-use restrictions.

`qmake()` creates `Queue` objects from channel declarations, assigning queue IDs, slot counts, field counts, field widths, backing storage, and step-number tracking. `qsend()` dispatches to asynchronous `a_snd()` or synchronous/rendezvous `s_snd()`. `qrecv()` handles normal queues via `a_rcv()` and has special nonblocking terminal input support for `STDIN`.

Asynchronous send appends or sorted-inserts messages (`sa_snd()`), casts fields to declared widths, records the producing depth, and respects `m_loss` for sends to full queues. Asynchronous receive tests constants and `eval()` constraints, supports random receive/poll variants, writes received values into target variables only on full receives, shifts queue contents after consuming, and emits arrows for MSC output. Rendezvous send stages a single-slot message, calls `complete_rendez()`, and coordinates sender/receiver trace output.

Output helpers `sr_talk()`, `docolumns()`, `difcolumns()`, `sr_buf()`, and `sr_mesg()` format ordinary traces, columnated output, xspin text, mtype names, and MSC/Tcl event labels. `qhide()`/`qishidden()` suppress selected queue output. `doq()` dumps visible queue state for globals/locals output.

Validation helpers catch unsafe channel operations and expression patterns. `nochan_manip()` rejects invalid channel assignments and records channel access. `no_internals()` prevents assignment to internal predefined variables. `scan_tree()` and `no_nested_array_refs()` detect array self-indexing patterns that can break generated verifier backing code.

Important risks: queue count is capped by `MAXQ`; queue IDs are one-based externally and zero-based internally; formatted printing uses a shared `Buf`; rendezvous state uses static remembered receiver pointers; and simulation behavior must match verifier code generated elsewhere.
