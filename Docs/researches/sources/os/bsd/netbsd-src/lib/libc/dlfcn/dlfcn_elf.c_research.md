# File Research: sources/os/bsd/netbsd-src/lib/libc/dlfcn/dlfcn_elf.c

Provides weak ELF `dlfcn` symbols in libc. Dynamic programs have these services resolved directly to the runtime linker; these definitions exist so static links or missing runtime linker services have linkable fallback symbols. `dlopen`, `dlsym`, and `dlvsym` return `NULL`; `dlclose` and `dlinfo` return `-1`; `dladdr` returns `0`; `dlerror` returns the static string "Service unavailable".

`dl_iterate_phdr` is the meaningful fallback. It lazily initializes static `dlpi_*` fields from `_dlauxinfo()` auxiliary-vector entries (`AT_BASE`, `AT_PHDR`, `AT_PHNUM`, `AT_SUN_EXECNAME`), adjusts the load address by scanning for `PT_PHDR`, uses producer/consumer memory barriers around the one-time setup flag, fills a `dl_phdr_info`, and invokes the caller callback once.

`___dl_cxa_refcount` is a no-op weak compatibility hook.

Dependencies include `<elf.h>`, `<sys/atomic.h>`, `rtld.h`, and weak alias support.

Risks/invariants: first-call setup can race but only stores pointer-sized or smaller fields. Static fallback dynamic-loading operations intentionally do not work.
