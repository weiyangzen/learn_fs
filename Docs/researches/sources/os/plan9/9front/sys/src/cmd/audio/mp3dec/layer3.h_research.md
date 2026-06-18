# File Research: sources/os/plan9/9front/sys/src/cmd/audio/mp3dec/layer3.h

This header exposes the single Layer III frame decoder entry point, `mad_layer_III(struct mad_stream *, struct mad_frame *)`. It includes `stream.h` and `frame.h` for the function signature.

`frame.c` uses this declaration in its decoder dispatch table, allowing generic frame decoding to call the Layer III implementation after parsing a frame header. All Layer III internals, including side-info structures, Huffman decode helpers, IMDCT helpers, and lookup tables, remain private in `layer3.c`.

The header is intentionally minimal. Its only role is to connect the shared frame pipeline to the large Layer III implementation.
