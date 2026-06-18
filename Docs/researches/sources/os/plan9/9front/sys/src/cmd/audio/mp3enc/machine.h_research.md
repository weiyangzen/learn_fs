# File Research: sources/os/plan9/9front/sys/src/cmd/audio/mp3enc/machine.h

## Scope
Machine/compiler compatibility layer for LAME internals.

## APIs and Data
Provides fallback C library declarations/macros, math includes, `POW20`/`IPOW20` lookup macros, inline portability definitions, `FLOAT`, `FLOAT8`, `sample_t`, and `stereo_t`.

## Dependencies
Includes `stdio.h`, `memory.h`, `math.h`, `ctype.h`, optional `errno.h`/`fcntl.h`, and system stat/type headers. Handles several legacy compiler/platform branches.

## Risks and Notes
`POW20`/`IPOW20` assume global tables exist elsewhere. Uses old portability branches and C++-style comments in places. `FLOAT8=float` is explicitly warned as breaking resampling and VBR code.
