# File Research: sources/os/plan9/plan9/sys/src/9/port/devmnt.c

Implements `#M`, the Plan 9 9P mount/client device. It multiplexes 9P RPCs over an underlying channel and presents remote files as local `Chan`s.

`mntversion` negotiates `Tversion` once per underlying channel, validates version/msize, creates a `Mnt`, sets `c->mux`, marks the channel `CMSG`, and creates the mount reply queue. `mntauth` and `mntattach` allocate local channels/fids and issue `Tauth`/`Tattach`.

Every filesystem operation creates or reuses an `Mntrpc`, assigns a unique tag, encodes an `Fcall`, writes it to the transport channel, and waits for the matching reply. `mountio` serializes readers through `m->rip` while allowing concurrent pending RPCs; `mountmux` matches replies by tag and wakes the owning request.

`mntrpcread` reads 9P message frames from the underlying channel into a queue, validates frame length against `msize`, decodes headers, and for `Rread` leaves data as blocks attached to the RPC. `mntrdwr` splits large reads/writes into `msize-IOHDRSZ` chunks and integrates with optional cache reads/writes.

Open/create, walk, stat, read, write, clunk, remove, and wstat map directly to 9P messages. Directory reads validate each returned stat record and call `mntdirfix` so local dev/type fields match the mounted channel.

Interrupt handling sends chained `Tflush` requests and marks unanswered RPCs as `Rflush`. `Mntrpc` headers and buffers are cached on a small free list; tags are allocated from a bitmask, excluding tag 0 and `NOTAG`.

The implementation depends on correct `Fcall` conversion, channel offsets for version negotiation, queue block handling, and tight lifetime rules between server channel `mchan`, local chans, and `Mnt`.
