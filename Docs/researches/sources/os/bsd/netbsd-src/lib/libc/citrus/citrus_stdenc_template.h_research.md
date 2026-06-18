# File Research: sources/os/bsd/netbsd-src/lib/libc/citrus/citrus_stdenc_template.h

Read completely: 206 lines.

This non-standalone template implements the standard-encoding module wrapper functions for concrete encodings. A module defines `_FUNCNAME`, `_ENCODING_INFO`, `_ENCODING_STATE`, `_ENCODING_MB_CUR_MAX`, and state-dependent hooks, then includes this header.

Generated behavior: `stdenc_getops` validates ABI version and ops length, `stdenc_init` allocates encoding info and calls module init, `stdenc_uninit` calls module uninit and frees closure, wrappers dispatch to module-private `mbrtowc_priv`, `wcrtomb_priv`, `stdenc_wctocs`, and `stdenc_cstowc`, and state reset/state description are delegated or defaulted based on module flags.

Important interactions: included by BIG5, DECHanyu, EUC, EUCTW, GBK2K, HZ, ISO2022, and JOHAB after each module defines its private state machine.

Security/reliability notes: this centralizes allocation and ABI-copy behavior. It assumes module-private functions observe the restartable conversion contract and that `nresult` is non-null. Failures in module init free the allocated closure.
