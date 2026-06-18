# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/skein.h

## Role

Declares the Skein hash API, context structures, optional extended initialization, tree/MAC support, and KCF mechanism metadata.

## Key Interfaces

- Return codes: `SKEIN_SUCCESS`, `SKEIN_FAIL`, `SKEIN_BAD_HASHLEN`.
- Defines state/block sizes for Skein-256, Skein-512, and Skein-1024.
- `Skein_Ctxt_Hdr_t` stores hash output bit length, buffered byte count, and two tweak words.
- Context structs for 256/512/1024 variants store common header, chaining variables, and aligned partial-block buffers.
- Incremental hash APIs: `Init`, `Update`, `Final`.
- Extended APIs: `InitExt`, `Final_Pad`, and, when enabled, `Output`.
- `skein_param_t` carries digest bit length for KCF hashing.
- Under `SKEIN_MODULE_IMPL`, defines mechanism strings, mechanism enum, and digest/MAC validation macros.

## Risk Notes

The context layout is algorithm-specific and may be copied for precomputed IV/MAC state reuse. Mechanism enum ranges are used by validation macros and must remain coherent.
