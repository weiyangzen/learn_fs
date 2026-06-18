# File Research: sources/os/plan9/9front/sys/src/cmd/vnc/exportfs.c

## Role

`exportfs.c` implements a compact concurrent 9P2000 server over the VNC server's synthetic `Dev` roots. It translates incoming 9P messages to `Chan` operations.

## Architecture

- `Export` owns the I/O fd, root channels, negotiated iounit, active work list, and fid hash table.
- `Fid` tracks a 9P fid, associated `Chan`, reference count, offset, and attached/clunked state.
- `Exq` is a queued request with message buffer, decoded `Fcall`, response suppression, and slave identity.
- Global `Exwork exq` queues requests across exporters and spawns worker processes as needed.

## Request Handling

- `sysexport()` builds an `Export` and runs `exportproc()`.
- `exportproc()` reads 9P messages, handles `Tflush` specially, queues other work, and starts `exslave()` workers.
- `exslave()` dequeues work, marks it in-progress for flush/shutdown visibility, dispatches through the `fcalls[]` table, encodes responses, and writes them unless flushed.
- `exflush()` can remove unstarted work or mark in-progress work as no-response and interrupt its worker.
- `exshutdown()` removes queued work and interrupts active work when the connection ends.

## Implemented 9P Operations

- `Tversion`: negotiates `9P2000` and clamps message size.
- `Tauth`: rejects auth as not required.
- `Tattach`: attaches to one of the exported roots by numeric attach name.
- `Twalk`: delegates to the device walk method and handles cloned fids.
- `Topen`, `Tcreate`, `Tread`, `Twrite`, `Tstat`, `Twstat`, `Tclunk`, and `Tremove`: delegate to the corresponding device methods with fid lifecycle handling.

## Notable Limitations And Risk Areas

- The fid table uses a small fixed hash size and manual reference bookkeeping.
- `Tread` stores `rpc->offset` in a `long`, so very large offsets are narrowed.
- `Tflush` may suppress a response after the worker has already written; the code accepts this race by design.
- Worker interruption depends on the compatibility-layer rendezvous interrupt mechanism.
