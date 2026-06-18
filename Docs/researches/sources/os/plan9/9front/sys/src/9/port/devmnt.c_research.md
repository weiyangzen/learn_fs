# File Research: sources/os/plan9/9front/sys/src/9/port/devmnt.c

Purpose: Implements the Plan 9 `#M` mount/client device, multiplexing 9P RPCs over an underlying server channel and presenting remote fids as local `Chan`s.

Key logic:
- `mntversion` performs the one-time `Tversion`/`Rversion` negotiation, clamps `msize`, installs `c->mux`, marks the channel `CMSG`, creates the input queue, and records the negotiated 9P version.
- `mntauth` and `mntattach` allocate local mount channels/fids, issue `Tauth`/`Tattach`, and bind returned qids to the server channel via `mchan`.
- Walk, stat, open/create, clunk/remove, wstat, read, write, bread, and bwrite are encoded as 9P requests through `Mntrpc`.
- `mountio`, `mntrpcread`, and `mountmux` serialize the transport reader while allowing multiple pending tags; replies are matched by tag and wake the owning RPC.
- `mntrdwr` chunks I/O by `c->iounit`, integrates with optional `CCACHE`, and fixes directory stat dev/type fields through `mntdirfix`.
- 9front adds deferred mount workers and `Mntrah` read-ahead support through `mntdefer`, `mntproc`, `rahproc`, and `mntrahread`.

Dependencies and integration:
- Depends on 9P `Fcall` conversion, `Queue` block I/O, channel refcounting/lifetime rules, cache helpers, and the generic Plan 9 `Dev` interface.

Risks and notes:
- Interrupt handling is subtle: interrupted RPCs allocate chained `Tflush` requests and then reconcile or abandon clunk/remove fids.
- `Mnt` lifetime is tied to the server channel refcount rather than a standalone `Mnt` refcount.
- Tag allocation excludes tag 0 and `NOTAG`; failed cleanup can strand pending requests.
