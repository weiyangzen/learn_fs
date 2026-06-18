# File Research: sources/os/plan9/9front/sys/src/cmd/audio/libvorbis/synthesis.c

Single-packet Vorbis PCM synthesis and packet blocksize helper implementation.

Important routines:
- `vorbis_synthesis()` validates decoder state, initializes packet bit reader, checks audio packet flag, reads mode/window flags, allocates block PCM storage, and dispatches mapping inverse.
- `vorbis_synthesis_trackonly()` parses packet mode/window/granule metadata without decoding PCM, useful for fast-forward tracking.
- `vorbis_packet_blocksize()` returns the decoded packet block size after reading the packet mode.
- `vorbis_synthesis_halfrate()` toggles half-rate decode mode if block size permits.
- `vorbis_synthesis_halfrate_p()` reports half-rate state.

Integration points:
- Uses `codec_internal.h`, `registry.h`, and `_mapping_P`.
- Relies on setup-header validation to make mode mapping/type indexes safe.
- Called from public libvorbis decode APIs declared in `vorbis/codec.h`.

Risk and review signals:
- `vorbis_synthesis()` has explicit null-state checks and returns `OV_EBADPACKET` for invalid decoder state.
- `vorbis_synthesis_trackonly()` assumes valid `vb`, `vd`, and backend state more directly than `vorbis_synthesis()`.
- Packet parsing rejects non-audio packets and invalid modes.
- PCM allocation uses block-local allocator.

Filesystem relevance:
- No filesystem logic. It decodes audio packets already supplied by container code.
