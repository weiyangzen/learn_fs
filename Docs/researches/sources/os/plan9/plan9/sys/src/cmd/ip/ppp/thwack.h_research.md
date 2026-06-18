# File Research: sources/os/plan9/plan9/sys/src/cmd/ip/ppp/thwack.h

Shared THWACK compressor/decompressor declarations and constants.

Key contents:
- Defines limits: `ThwMaxBlock`, hash size, minimum match, encoder/decoder window sizes, sequence-mask sizes, and stats count.
- `ThwBlock` stores encoder history metadata, hash table pointer, and source data pointer.
- `Thwack` stores encoder lock, current slot, block metadata, per-slot hash tables, and retained source `Block*`.
- `UnthwBlock` and `Unthwack` store decoder history and fixed decode buffers.
- Declares encoder/decoder APIs: init, cleanup, encode, ack, decode, state, and add-uncompressed-block.

Integration:
- Included by PPP THWACK integration and encoder/decoder implementations.
- Depends on Plan 9 `Block` and `QLock` types via including contexts.

Risks and notes:
- The constants encode the wire format assumptions; compressor and decompressor must stay in lockstep.
