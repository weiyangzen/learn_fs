# File Research: sources/os/plan9/9front/sys/src/cmd/audio/libvorbis/floor0.c

Vorbis floor backend 0 implementation. Floor0 reconstructs a spectral envelope from line spectral pairs decoded from codebooks.

Important routines:
- `floor0_free_info()` and `floor0_free_look()` release floor0 setup and lookup state.
- `floor0_unpack()` reads floor0 setup from an Ogg bitpack buffer: order, rate, Bark map size, amplitude bit fields, amplitude dB range, and codebook list. It validates book indexes and rejects maptype-0 books.
- `floor0_map_lazy_init()` lazily builds linear-frequency to Bark-scale maps per block size.
- `floor0_look()` creates the runtime lookup containing order, Bark map length, and lazy linear maps.
- `floor0_inverse1()` decodes amplitude and LSP vector values from the packet, cumulatively reconstructing LSP coefficients.
- `floor0_inverse2()` maps the LSP envelope to a spectral curve with `vorbis_lsp_to_curve()`, or clears output when no floor is present.
- `floor0_exportbundle` exposes the backend hooks to the registry.

Integration points:
- Uses `lpc.h`, `lsp.h`, `codebook.h`, `scales.h`, and Vorbis backend registry types.
- Called by setup-header unpack through `_floor_P`.
- Decode-time mapping uses `inverse1` and `inverse2` through `mapping0.c`.

Risk and review signals:
- Uses `_vorbis_block_alloc()` for packet-local LSP memory.
- Lazy map initialization assumes `look->linearmap` is valid and block sizes are already validated.
- Floor0 is decode-oriented here; export bundle has no pack hook.

Filesystem relevance:
- No filesystem logic. It is Vorbis audio decode backend code.
