# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gsdllos2.h

## Role

`gsdllos2.h` adds OS/2-specific declarations for the old Ghostscript DLL interface.

## API

Declares exported load-time function:

- `gsdll_get_bitmap(unsigned char *device, unsigned char **pbitmap)`

Defines runtime dynamic-linking typedef:

- `PFN_gsdll_get_bitmap`

## Dependencies

Relies on old DLL calling-convention macro `GSDLLAPI` being available before inclusion. It does not include `gsdll.h` directly.

## Integration Notes

This is a narrow platform extension used by OS/2 clients to retrieve a bitmap pointer from a named/device handle under the old DLL interface.

## Risks

The exported function declaration returns `unsigned long`, while the typedef returns `long`. On platforms where signedness/width differ in ABI-significant ways, this mismatch is worth checking.
