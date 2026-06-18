# File Research: sources/os/bsd/netbsd-src/lib/libc/string/strxfrm.c

Implements `strxfrm()` and `strxfrm_l()`. Because LC_COLLATE is not implemented here, transformation is just a bounded string copy suitable for `strcmp()` equivalence.

The function returns the full source length regardless of destination size, matching `strxfrm` sizing semantics.
