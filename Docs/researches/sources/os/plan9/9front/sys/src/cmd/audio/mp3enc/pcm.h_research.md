# File Research: sources/os/plan9/9front/sys/src/cmd/audio/mp3enc/pcm.h

## Scope
Interface and constants for the generalized PCM/resampling layer.

## APIs and Data
Defines encoder delay/resampling constants, object IDs, floating typedefs, scalar function pointer types, data direction annotation macros, PCM layout flags (`LAME_INTERLEAVED`, `LAME_CHAINED`, `LAME_INDIRECT`), endian flags, PCM sample type flags, and channel-count flags. Declares scalar function pointers and possible i387/3DNow/SIMD/plain implementations, resampler lifecycle functions, `init_scalar_functions`, `unround_samplefrequency`, and `lame_encode_ogg_frame`.

## Dependencies
Includes `limits.h`, `lame.h`, and `util.h`.

## Risks and Notes
Defines `inline` as `__inline`, which can affect includers. The header assumes `CHAR_BIT == 8` and emits preprocessor diagnostics otherwise. Many declared optimized scalar implementations are platform/build dependent.
