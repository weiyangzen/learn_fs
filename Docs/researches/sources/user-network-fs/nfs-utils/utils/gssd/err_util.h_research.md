<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-utils/utils/gssd/err_util.h -->
# sources/user-network-fs/nfs-utils/utils/gssd/err_util.h

## Purpose
This header exposes gssd logging helpers and the diagnostic seconds-to-time formatter.

## APIs And Types
It declares `initerr`, `printerr`, `get_verbosity`, and `sec2time`. `printerr` carries a GCC printf-format attribute so callers get compile-time checking for format strings and arguments.

## State, Dependencies, And Integration
The header has no state but represents the public logging contract implemented in `err_util.c`. It is included by most gssd modules and context backends, so changes affect both client and server GSS daemon builds.

## Risks And Test Signals
Risks include the unconditional `__attribute__` portability assumption and the static-buffer semantics of `sec2time` not being visible in the prototype. Test with compilers that support or reject GCC attributes, format warning builds, and concurrent diagnostic use.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-utils/utils/gssd/err_util.h -->
