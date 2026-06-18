# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevdsp2.h

Internal display device structure header.

Key contents:
- Declares `gx_device_display`.
- Defines common fields: backing memory device, callback pointer, handle, format, bitmap pointer/size, resolution flag, DeviceN params, equivalent CMYK colors.
- Defines GC descriptor macro `public_st_device_display()` used by `gdevdsp.c`.

Risks / notes:
- Layout couples tightly to Ghostscript device and GC relocation machinery.
