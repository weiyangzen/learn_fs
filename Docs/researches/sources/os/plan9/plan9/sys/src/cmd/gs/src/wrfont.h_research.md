# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/wrfont.h

Header for font serialization output helpers.

Key points:
- Includes `stdpre.h`.
- Defines `WRF_output` with current output pointer, buffer limit, total count, encryption flag, and eexec key.
- Declares byte/text/string/float/int writer functions.
- Comments explain the output is intended to be passed to FreeType through the FAPI FreeType bridge.

Dependencies and interactions:
- Consumed by Type 1 and Type 2 serialization implementations.

Research relevance:
- Defines the small output abstraction used by FAPI font serializers.
