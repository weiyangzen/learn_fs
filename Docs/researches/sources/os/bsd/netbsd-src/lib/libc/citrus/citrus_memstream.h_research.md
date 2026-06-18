# File Research: sources/os/bsd/netbsd-src/lib/libc/citrus/citrus_memstream.h

Inline API and struct definition for Citrus memory streams.

Key behavior:
- Defines `_citrus_memory_stream` with a region and current offset.
- Declares line/match/chr/skip helpers.
- Provides inline bind, bind pointer, rewind, tell, remainder, seek, getc, ungetc, peek, getregion, typed get8/get16/get32, and get-line-as-region helpers.

Notable detail:
- `_citrus_memory_stream_get8` checks for one byte but advances `ms_pos` by 2. This is unusual and may be a latent typo unless callers rely on 2-byte stepping; the surrounding get16/get32 advance by their natural sizes.
