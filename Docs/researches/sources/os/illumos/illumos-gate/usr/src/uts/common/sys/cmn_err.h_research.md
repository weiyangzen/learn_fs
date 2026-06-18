# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/cmn_err.h

This header declares kernel diagnostic printing interfaces. Severity constants include continuation, note, warning, panic, and ignore.

It exports `cmn_err`, zone-aware variants, device-aware variants, `printf`/`zprintf`/`uprintf`, `snprintf`/`sprintf` variants, and `panic`/`vpanic`, with `__KPRINTFLIKE`, `__KVPRINTFLIKE`, and printf-like annotations.
