# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/bl.h

This is a private FMA blacklist ioctl interface. It defines `BLIOC_INSERT` and `BLIOC_DELETE`, plus `bl_req_t`, which carries a packed FMRI buffer, FMRI size, and event-class reason string. A 32-bit syscall form `bl_req32_t` is provided under `_SYSCALL32`.

`BL_FMRI_MAX_BUFSIZE` caps packed FMRI size at 8192 bytes. Kernel builds also expose `blacklist(int, const char *, nvlist_t *, const char *)`.
