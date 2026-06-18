# File Research: sources/os/bsd/netbsd-src/lib/libc/stdio/fgetwc.c

Read completely: 102 lines.

This file implements `fgetwc` and unlocked internal `__fgetwc_unlock`. It sets wide orientation, returns pending `ungetwc` characters first, refills byte buffers as needed, converts bytes with `mbrtowc`, maintains input conversion state, and advances stream pointers.

Important interactions: used by wide line/string input and depends on `WCIO_GET`, `__srefill`, and locale multibyte conversion state.

Security/reliability notes: invalid multibyte input sets `__SERR`; incomplete sequences consume current buffered bytes and retry after refill.
