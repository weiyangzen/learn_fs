# File Research: sources/os/plan9/9front/sys/src/cmd/ip/ppp/thw.c

This file adapts the Thwack compressor/decompressor to PPP CCP. It provides `Comptype cthwack` and `Uncomptype uncthwack`, which match the vtable interface declared in `ppp.h`.

The compressor state `Cstate` tracks a sequence number, a `Thwack` encoder, and stats. The decompressor state `Uncstate` tracks acknowledgment scheduling, reset state, and an `Unthwack` decoder.

`comp` wraps PPP payloads into `Pcdata` compressed datagrams. It prepends compressed protocol fields, embeds decompressor acknowledgments when available, decides whether small packets must be added to history, and falls back to uncompressed output when compression is not worthwhile or does not fit the MTU.

`uncomp` decodes Thwack data frames, uncompressed-add frames, and plain uncompressed frames. On decoder errors it sends CCP Reset-Request and marks the decompressor inactive until the matching Reset-Ack arrives. It also derives ACK masks from the decoder history and feeds incoming ACKs back to the compressor via `thwackack`.

`compresetreq` resets the encoder and converts a peer Reset-Request into Reset-Ack. `uncresetack` reactivates and resets the decoder after the expected reset id.

The file is glue code: sequence, ACK, reset, and PPP protocol-field handling live here; the actual LZ/Huffman-style codec lives in `thwack.c` and `unthwack.c`.
