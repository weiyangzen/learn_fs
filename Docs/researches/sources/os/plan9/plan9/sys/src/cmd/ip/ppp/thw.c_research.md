# File Research: sources/os/plan9/plan9/sys/src/cmd/ip/ppp/thw.c

PPP integration layer for the THWACK compressor/decompressor.

Key behavior:
- Defines compressor state `Cstate` and decompressor state `Uncstate`.
- Exposes `Comptype cthwack` and `Uncomptype uncthwack` hooks for the PPP stack.
- `comp()` prepends compressed PPP protocol and optional acknowledgment fields, calls `thwack()`, and falls back to uncompressed packets when compression is not worthwhile or MTU would be exceeded.
- `uncomp()` decodes THWACK packet classes: compressed, uncompressed, and uncompressed-add-to-window.
- Maintains ack sequence/mask feedback from decompressor to compressor.
- Issues LCP reset requests on decompression corruption and processes reset acks to reactivate the decompressor.

Integration:
- Depends on `ppp.h` block/LCP helpers and `thwack.h` compressor primitives.
- Uses PPP CCP data protocol `Pcdata`.
- Interacts with peer reset packets through `alloclcp(Lresetreq/Lresetack, ...)`.

Risks and notes:
- Header space is assumed available and calls `sysfatal()` if not.
- Corruption handling deactivates decompression until reset acknowledgment.
- Acks are protected with `QLock`, but sequence state is simple and assumes PPP control flow correctness.
