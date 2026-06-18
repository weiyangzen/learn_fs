# File Research: sources/os/bsd/netbsd-src/lib/libc/citrus/citrus_mapper.h

Public internal interface and inline dispatchers for Citrus mappers.

Key behavior:
- Declares mapper area creation, open, direct open, close, and persistent marking.
- Defines conversion result constants for success, non-identical mapping, source-more, destination-more, illegal sequence, and fatal errors.
- Provides inline wrappers for convert, init state, state size, source max, and destination max.
- Includes `citrus_mapper_local.h` for structure definitions.

This is the generic mapping API used by charset mapping and serial mapper composition.
