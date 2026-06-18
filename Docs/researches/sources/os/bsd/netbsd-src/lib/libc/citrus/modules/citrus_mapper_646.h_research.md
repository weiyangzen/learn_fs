# File Research: sources/os/bsd/netbsd-src/lib/libc/citrus/modules/citrus_mapper_646.h

Read completely: 37 lines.

This header declares the mapper_646 getops entry point twice with `_CITRUS_MAPPER_GETOPS_FUNC(mapper_646)`.

Security/reliability notes: duplicate identical declarations are harmless in C but noisy; declaration-only ABI surface otherwise.
