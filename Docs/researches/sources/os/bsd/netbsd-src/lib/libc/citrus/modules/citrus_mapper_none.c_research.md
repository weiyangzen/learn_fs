# File Research: sources/os/bsd/netbsd-src/lib/libc/citrus/modules/citrus_mapper_none.c

Read completely: 111 lines.

This module implements the identity mapper. Initialization sets traits to stateless 1:1 conversion with no closure. Conversion writes `src` to `*dst` and returns `_CITRUS_MAPPER_CONVERT_SUCCESS`.

Important interactions: useful as a mapper plugin where an explicit no-op mapping is needed. It exports through mapper ABI macros.

Security/reliability notes: no dynamic allocation and minimal attack surface. The convert function assumes `dst` is valid.
