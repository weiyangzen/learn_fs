# File Research: sources/os/plan9/9front/sys/src/cmd/audio/libvorbis/mapping0.c

Vorbis channel mapping backend 0 implementation. It wires floor, residue, psychoacoustic analysis, coupling, quantization, and MDCT together for encode and decode.

Important routines:
- `mapping0_free_info()` releases mapping setup.
- `mapping0_pack()` writes submapping, coupling, channel mux, floor submap, and residue submap setup fields.
- `mapping0_unpack()` reads and validates mapping setup, including channel count, coupling pairs, reserved bits, submap indexes, floor indexes, and residue indexes.
- `mapping0_forward()` is the main encode path:
  - windows PCM,
  - runs MDCT and FFT,
  - computes log spectral data,
  - builds noise and tone masks,
  - fits floor1 curves,
  - creates bitrate-managed floor variants across `PACKETBLOBS`,
  - writes packet mode/window flags,
  - encodes floors,
  - performs psychoacoustic coupling/quantization/normalization,
  - classifies and encodes residue by submap.
- `mapping0_inverse()` is the main decode path:
  - decodes floor memo per channel,
  - marks nonzero channels,
  - decodes residue bundles,
  - reverses channel coupling,
  - applies floor curves,
  - runs inverse MDCT.
- `mapping0_exportbundle` registers pack/unpack/free/forward/inverse hooks.

Integration points:
- Uses `codec_internal.h`, `window.h`, `registry.h`, `psy.h`, `mdct.h`, `envelope.h`, `lpc.h`, `lsp.h`, and `scales.h`.
- Directly assumes encode-side floor backend is floor1; it returns `-1` if configured floor type is not 1.
- Calls residue backend class/forward/inverse hooks from `_residue_P`.

Risk and review signals:
- Allocates several temporary arrays with plain `malloc()` and no allocation checks.
- Encode mode selection uses `int modenumber=vb->W`, assuming setup mode ordering matches short/long block choice.
- Coupling decode mutates channel spectral vectors in reverse coupling order and depends on validated coupling pairs.
- The disabled analysis block contains a duplicate floor dB table for debugging only.
- Good tests should include mono/stereo/multichannel mappings, coupling edge cases, zero floor channels, managed bitrate blobs, and malformed mapping headers.

Filesystem relevance:
- No filesystem logic. It is the central Vorbis audio packet mapping backend.
