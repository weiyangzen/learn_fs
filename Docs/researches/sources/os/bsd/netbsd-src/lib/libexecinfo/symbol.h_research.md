# File Research: sources/os/bsd/netbsd-src/lib/libexecinfo/symbol.h

## Purpose
Architecture abstraction for canonicalizing function-symbol addresses.

## Main Content
- Declares `symbol_canonicalize_md()` when `__HAVE_FUNCTION_DESCRIPTORS` is defined.
- Defines `SYMBOL_CANONICALIZE(x)` to call the machine-dependent implementation for descriptor architectures, or cast directly to `uintptr_t` otherwise.

## Integration
Used by `backtrace.c` and `symtab.c` before comparing symbol addresses and offsets.

## Risks / Notes
Architectures with function descriptors must provide a matching `symbol_${arch}.c`; otherwise symbol offsets may be wrong.
