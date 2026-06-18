# File Research: sources/os/plan9/9front/sys/src/cmd/audio/libFLAC/share/private.h

## Role

`share/private.h` declares unpublished debug/control routines from libFLAC. It is intended only for code shipped with FLAC, not external clients.

## API Surface

It declares APIs to disable instruction-set dispatch, constant subframes, fixed subframes, and verbatim subframes on a stream encoder. It also declares setters/getters for the encoder's MD5 behavior.

## Risks / Edge Cases

Although marked `FLAC_API`, these are explicitly unpublished private routines. External consumers using them would couple to unstable internals.

## Dependencies

The header assumes `FLAC_API`, `FLAC__bool`, and `FLAC__StreamEncoder` are already declared by included public FLAC headers in the translation unit.
