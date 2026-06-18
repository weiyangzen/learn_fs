# File Research: sources/os/plan9/9front/sys/src/cmd/audio/mp3dec/frame.h

This header defines MPEG frame/header types and constants. It declares `enum mad_layer`, `enum mad_mode`, and `enum mad_emphasis`, plus `struct mad_header` for parsed metadata and `struct mad_frame` for decoded subband samples and Layer III overlap state.

Important macros include `MAD_NCHANNELS`, which maps single-channel mode to one channel and all other modes to two, and `MAD_NSBSAMPLES`, which returns 12, 18, or 36 subband sample groups depending on layer and LSF status. The flags enum records protection, padding, stereo mode features, free format, LSF, multichannel extension, MPEG 2.5, and incomplete-header status. Private bit constants separate header private data from Layer III private bits.

The public API initializes/finishes headers and frames, decodes a header, decodes a full frame, and mutes a frame. It depends on `fixed.h` and `stream.h`, and is consumed by the decoder orchestrator, layer decoders, and the Plan 9 frontend's header callback.
