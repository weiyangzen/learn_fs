# File Research: sources/os/plan9/plan9/sys/src/cmd/spin/mesg.c

## Purpose

`mesg.c` implements Spin’s runtime/simulation handling for Promela channels and messages. It manages channel queue allocation, asynchronous and rendezvous sends/receives, queue inspection, message trace output, and semantic checks that prevent invalid channel manipulation in Promela expressions.

## Main Responsibilities

- Creates queue instances for `chan` initializers through `qmake`.
- Maintains global queue registries:
  - `qtab`: linked list of all queues.
  - `ltab[MAXQ]`: direct queue lookup by one-based queue id.
  - `nqs`: number of allocated queue types/instances.
- Implements channel predicates:
  - `qfull`
  - `qlen`
  - `q_is_sync`
- Executes send/receive operations:
  - `qsend`
  - `qrecv`
  - `a_snd` for buffered channels.
  - `s_snd` for rendezvous channels.
  - `a_rcv` for receive/poll/test behavior.
  - `sa_snd` for sorted send insertion.
- Emits trace/debug output for Spin, XSpin, and columnated traces.
- Dumps queue contents for simulation display.
- Checks invalid channel assignments and risky array self-indexing.

## Important Data Flow

`qmake(Symbol *s)` is the creation path. If a symbol initializer is a `CHAN`, it allocates a `Queue`, assigns a one-based `qid`, records slot count and field count, allocates `contents`, `fld_width`, and `stepnr`, then stores the queue in both `qtab` and `ltab`.

`qsend(Lextok *n)` evaluates the channel expression, maps it to `ltab[whichq]`, and chooses buffered or rendezvous send based on `nslots`.

`qrecv(Lextok *n, int full)` evaluates the channel expression and calls `a_rcv`. It special-cases `STDIN` as pseudo-channel id zero when the channel evaluates to uninitialized id `-1`.

Buffered receive first checks executability by matching constants and `eval(...)` receive arguments. For non-FIFO random receive forms, it can scan later queue slots. If `full` is true and the operation is not a poll, it assigns received values and shifts the queue down.

Rendezvous send temporarily stores message fields in the zero-slot queue, calls `complete_rendez()`, and only commits the synchronized send if a matching receive exists.

## Key Functions

- `cnt_mpars`: counts message fields, expanding compound field declarations through `Cnt_flds`.
- `qmake`: allocates and initializes queue metadata and storage.
- `qfull`, `qlen`, `q_is_sync`: queue predicates used by Promela expressions.
- `qsend`: public send dispatcher.
- `qrecv`: public receive dispatcher plus `STDIN` support.
- `sa_snd`: sorted insertion point and slot shift for sorted sends.
- `typ_ck`: optional type-clash warning for channel-related fields.
- `a_snd`: buffered send implementation.
- `a_rcv`: buffered receive, poll, and executability test implementation.
- `s_snd`: rendezvous send implementation.
- `channm`: builds printable channel names, including struct/array references.
- `docolumns`, `difcolumns`, `sr_talk`, `sr_buf`, `sr_mesg`: trace formatting.
- `doq`: prints queue contents for a channel symbol.
- `qhide`, `qishidden`: suppress trace output for selected channels.
- `nochan_manip`: rejects invalid use/assignment of channel names and tracks accesses.
- `newbasename`, `delbasename`, `checkindex`, `scan_tree`, `no_nested_array_refs`: detect array self-index patterns such as `a[a[1]]`.
- `no_internals`: blocks assignments to internal system variables `_nr_pr` and `_p`.

## Dependencies

The file depends heavily on Spin’s AST and symbol infrastructure from `spin.h` and `y.tab.h`, including `Lextok`, `Symbol`, `Queue`, `RunList`, `eval`, `setval`, `cast_val`, `Sym_typ`, `Width_set`, `getuname`, `complete_rendez`, `pstext`, `whoruns`, `fatal`, and `non_fatal`.

Global flags such as `verbose`, `TstOnly`, `s_trail`, `analyze`, `columns`, `depth`, `xspin`, `m_loss`, and `jumpsteps` alter both semantics and reporting.

## Notable Behavior

- Queue ids are one-based externally and zero-based in `ltab`.
- Zero-slot channels are still allocated with one storage slot internally so rendezvous values can be staged.
- `m_loss` controls behavior when a buffered send targets a full queue.
- `TstOnly` makes send/receive paths act as executability tests without mutating queue state.
- `n->val` selects variants such as sorted send, FIFO/random receive, and poll behavior.
- `columns == 2` produces MSC-style differential column traces through `pstext` and `putarrow`.
- The predefined variable `_` is treated specially in rendezvous trace output as a write-only placeholder.

## Risks and Maintenance Notes

This is old C with fixed-size local buffers and repeated `strcat`/`sprintf` use. Most inputs are Promela identifiers or generated/internal strings, but the code assumes those upstream constraints hold.

`sr_mesg` uses `fprintf(fd, Buf)` instead of `fprintf(fd, "%s", Buf)`. In normal Spin usage `Buf` is built from numbers or mtype identifiers, but the pattern is still fragile.

The channel semantics are tightly coupled to global interpreter state. Any change to `TstOnly`, rendezvous bookkeeping, or receive variants needs regression coverage across buffered channels, zero-slot rendezvous channels, sorted send, poll, and trail replay output.

## Filesystem Relevance

No filesystem implementation logic is present. Filesystem interaction is limited to stdout/stderr style reporting; this file is relevant only because it is part of the Plan 9 source tree.
