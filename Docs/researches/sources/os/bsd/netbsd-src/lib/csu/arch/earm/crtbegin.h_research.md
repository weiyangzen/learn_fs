# File Research: sources/os/bsd/netbsd-src/lib/csu/arch/earm/crtbegin.h

EABI ARM `crtbegin` header. It marks constructor/destructor helper functions with C constructor/destructor attributes for array-based startup.

For static non-DWARF-EH builds it also defines `find_exidx`, returns the ARM unwind index range, and weak-aliases it to `__gnu_Uwind_find_exidx`.
