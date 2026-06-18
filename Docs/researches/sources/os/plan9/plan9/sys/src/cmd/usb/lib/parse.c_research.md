# File Research: sources/os/plan9/plan9/sys/src/cmd/usb/lib/parse.c

USB descriptor parser.

Main functions:
- `parsedev` validates and unpacks the standard device descriptor into `Usbdev`.
- `parseiface` creates/fills `Iface` and alternate setting state.
- `parseendpt` creates/fills `Ep`, handles direction, type, isochronous attributes, max packet, high-speed transactions, and interface endpoint lists.
- `parsedesc` walks mixed descriptors following a configuration descriptor, dispatching standard interface/endpoint descriptors and storing unknown/device-specific descriptors with context.
- `parseconf` validates and unpacks the standard configuration descriptor, then parses the remaining descriptor stream.

Important details:
- If a device-level CSP is zero, the first interface CSP becomes the device CSP.
- Device-specific descriptors preserve links to current config/interface/endpoint/alt setting for drivers such as CDC Ethernet and hubs.
- Handles endpoint ID sharing for IN/OUT by marking direction `Eboth`.

This parser populates the descriptor model consumed by all drivers.
