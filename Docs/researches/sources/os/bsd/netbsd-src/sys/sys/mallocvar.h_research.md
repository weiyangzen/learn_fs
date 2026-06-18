# File Research: sources/os/bsd/netbsd-src/sys/sys/mallocvar.h

Defines the placeholder malloc type interface. It forward-declares `struct malloc_type`; in kernel builds, `MALLOC_DECLARE` creates an unused static null pointer and define/attach/detach macros are no-ops.

This preserves compile-time compatibility with older typed malloc call sites. Risks are mainly expectations mismatch: consumers cannot rely on per-type allocation statistics or runtime registration from these macros.
