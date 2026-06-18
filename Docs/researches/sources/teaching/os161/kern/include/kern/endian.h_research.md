# File Research: sources/teaching/os161/kern/include/kern/endian.h

User/kernel-shared endian constants.

Key contents:
- Defines historical BSD byte-order constants `_LITTLE_ENDIAN`, `_BIG_ENDIAN`, `_PDP_ENDIAN`.
- Includes machine-specific `<kern/machine/endian.h>` to define `_BYTE_ORDER`.

Relevance:
- Forms the exported ABI layer used by kernel `<endian.h>` and userland networking/endian headers.
