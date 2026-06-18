# File Research: sources/os/bsd/dragonflybsd/sys/sys/socketvar.h

This header defines DragonFly kernel socket state, signaling socket buffers, socket state bits, sysctl-exported socket records, socket buffer predicates, socket options, accept filters, and socket/file operation declarations.

Key responsibilities:
- Defines `struct signalsockbuf`, embedding `struct sockbuf` and adding:
  - kqueue info
  - pending notification message list
  - atomic flags
  - timeout, low/high water marks, mbuf max
  - frontend/backend token
- Defines `SSB_*` flags:
  - lock/wait/async/upcall/nointr/knote/message event/stop/autosize/autolowat/wakeup/prealloc/stopsupp
- Defines `SSB_CLEAR_MASK` and `SSB_NOTIFY_MASK`.
- Defines kernel `struct socket`:
  - type/options/linger/state
  - protocol PCB and protocol switch pointer
  - accept queue head/back pointer/listing fields
  - message port/original port
  - errors, async I/O, OOB mark
  - receive/send `signalsockbuf`
  - upcall, credentials, emulator data, refs
  - accept filter data
  - close and received netmsgs
  - foreign address
  - socket inode and user cookie
- Defines socket state bits `SS_*`.
- Defines sysctl-exported `struct xsocket` and nested `struct xsockbuf`.
- Defines macros:
  - `sosendallatonce()`
  - `soreadable()`
  - `sowriteable()`
  - `ssb_append*()` wrappers
  - kqueue note insertion/removal
  - `sorwakeup()`/`sowwakeup()`
- Defines inline `ssb_space()` and `ssb_space_prealloc()`.
- Defines inline `ssb_preallocstream()`.
- Defines kernel `struct sockopt` and `enum sopt_dir`.
- Defines `struct accept_filter`.
- Declares socket malloc types, globals, file operations, socket buffer functions, socket lifecycle/state functions, option copy helpers, send/receive variants, wakeup, export, and accept-filter APIs.

Important invariants:
- `SSB_STOP` makes `ssb_space()` report zero regardless of byte/mbuf counters.
- Preallocation-aware space uses the tighter of actual and preallocated availability.
- `soreadable()` considers data, receive shutdown, completed accept queue, and socket errors.
- `sowriteable()` considers send buffer space, connection state/protocol flags, send shutdown, and error.
- `SS_NOFDREF` and `so_pcb` state are explicitly interlocked with `so_refs`.
- `signalsockbuf` partial clearing is sensitive to `sorflush()` and `sowflush()` implementation details.

Research notes:
- This is the central kernel socket object contract and is tightly coupled to DragonFly's netmsg/lwkt token design.
