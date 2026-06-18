# File Research: sources/os/plan9/9front/sys/src/cmd/audio/libvorbis/codec_internal.h

Internal libvorbis codec state header. It defines private encoder/decoder structures and declares floor1 encode-side helpers shared across backend files.

Important contents:
- Defines block-type constants, `PACKETBLOBS`, and `vorbis_block_internal`, which stores delayed PCM, maximum amplitude, block type, and bitrate-managed packet blobs.
- Defines internal opaque aliases for floor, residue, and transform lookups.
- Defines `vorbis_info_mode`, the packed mode description containing block flag, window type, transform type, and mapping index.
- Defines `private_state`, the runtime codec backend state hanging off `vorbis_dsp_state`: envelope lookup, window cache, MDCT/FFT lookups, floor/residue/psychoacoustic lookups, temporary header packet storage, bitrate manager state, and sample count.
- Defines `codec_setup_info`, the central setup structure containing block sizes, modes, mappings, floor/residue/codebook descriptors, full runtime codebooks, psychoacoustic setup, bitrate manager info, high-level encoder setup, and decode halfrate flag.
- Defines `vorbis_look_floor1`, the floor1 lookup structure used by `floor1.c` and declared encode-side helpers.

Integration points:
- Included widely by libvorbis internals such as `info.c`, `mapping0.c`, `envelope.c`, `floor0.c`, and `floor1.c`.
- `info.c` allocates and clears `codec_setup_info`.
- `block.c` and mapping/floor/residue backends consume `private_state` and setup arrays.
- `floor1_fit()`, `floor1_interpolate_fit()`, and `floor1_encode()` are declared here for encoder use from `mapping0.c`.

Risk and review signals:
- This is a private ABI within the vendored libvorbis tree; field layout changes affect many C files.
- Array sizes are fixed by Vorbis limits: 64 modes/maps/floors/residues, 256 books, and 4 psychoacoustic configs.
- Many pointers are owned elsewhere; cleanup correctness depends on `vorbis_info_clear()` and backend-specific free hooks.

Filesystem relevance:
- No filesystem logic. This is vendored audio codec internal state under 9front audio command sources.
