# File Research: sources/virtualization/nvme-cli/libnvme-wrap.c

This file defines wrapper macros for weak libnvme function forwarding.

Core behavior:
- Includes `dlfcn.h`, `errno.h`, `stdlib.h`, `libnvme.h`, and `nvme-print.h`.
- `VOID_FN` generates a weak wrapper for a void-returning function. It resolves the next symbol with `dlsym(RTLD_NEXT, name)`, reports an error, and exits if missing.
- `FN` generates a weak wrapper for a returning function. It resolves the next symbol and returns a default value if unavailable.

Integration role:
- Allows nvme-cli to provide compatibility wrappers around libnvme symbols while still forwarding to the real implementation when present.
- Useful when source compatibility must tolerate libnvme version differences.
