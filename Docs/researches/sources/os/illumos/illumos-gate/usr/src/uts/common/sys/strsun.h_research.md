# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/strsun.h

`strsun.h` exposes Solaris DDI STREAMS utility macros and kernel helper prototypes for working with `mblk_t`/`dblk_t`. It includes `stream.h` and `types.h`.

The macros provide stable access to data-block base/limit/ref/type/flags and message geometry: `MBLKL()` for bytes currently in an mblk, `MBLKSIZE()` for data-buffer capacity, `MBLKHEAD()` for headroom, `MBLKTAIL()` for tailroom, and `MBLKIN()` to validate a range inside the readable message data.

Kernel-only helper declarations cover STREAMS ioctl copy helpers (`mcopyin`, `mcopyout`, `mcopymsg`), error and ioctl acknowledgment helpers (`merror`, `mioc2ack`, `miocack`, `miocnak`, `miocpullup`), message exchange (`mexchange`), and message sizing (`msgsize`).

This header is the supported utility layer over selected `stream.h` internals, contrasting with `strsubr.h`, which is private implementation detail.
