# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/xti_xtiopt.h

`xti_xtiopt.h` defines generic XTI-level option constants and the linger option structure. It includes `sys/types.h` for `t_scalar_t`.

`XTI_GENERIC` is the generic XTI option level. Defined options include debugging, linger-on-close, receive buffer size, receive low-water mark, send buffer size, and send low-water mark. `struct t_linger` carries on/off state and linger duration.

As with the other XTI headers in this group, comments note that XTI headers expose some options to satisfy specification assertions and legacy compatibility, not necessarily because every option is independently implemented by every transport.
