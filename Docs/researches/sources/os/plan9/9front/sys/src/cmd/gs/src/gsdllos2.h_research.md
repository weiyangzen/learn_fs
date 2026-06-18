# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gsdllos2.h

This small header extends the old DLL interface for OS/2.

It declares:
- `gsdll_get_bitmap`, returning bitmap access for a device.
- `PFN_gsdll_get_bitmap`, the runtime dynamic-link function pointer type.

It depends on calling conventions such as `GSDLLAPI` being available from the core DLL headers or platform build configuration.
