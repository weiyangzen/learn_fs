# File Research: sources/os/plan9/9front/sys/src/cmd/audio/mp3dec/layer12.h

This header exposes the Layer I and Layer II decoder entry points: `mad_layer_I` and `mad_layer_II`. Both take a `struct mad_stream *` and `struct mad_frame *`, reading compressed frame data from the stream and filling the frame's subband sample array.

It includes `stream.h` and `frame.h` because those structures are part of the function signature. `frame.c` uses this header to populate its layer dispatch table, mapping MPEG header layer values to the correct decoder implementation.

There are no data definitions or helper declarations here. Internal Layer I/II lookup tables and helper routines stay private in `layer12.c`, keeping the public surface narrow.
