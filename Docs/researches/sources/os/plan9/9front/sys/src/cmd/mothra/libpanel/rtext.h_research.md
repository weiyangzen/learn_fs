# File Research: sources/os/plan9/9front/sys/src/cmd/mothra/libpanel/rtext.h

Defines rich-text special spacing encodings.

Key behavior:
- Defines bit layout for negative special spacing values.
- Provides macros to create/decode special values and their arguments.
- Defines `PL_TAB` as tab-stop spacing before text.
- Declares `pltabsize()`.

Important dependencies: `rtext.c`.

Notable risks:
- Special spacing values are encoded into signed integers; callers must use macros consistently.
