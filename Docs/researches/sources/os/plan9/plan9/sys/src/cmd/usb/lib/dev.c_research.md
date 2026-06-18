# File Research: sources/os/plan9/plan9/sys/src/cmd/usb/lib/dev.c

Core USB device and endpoint helper implementation.

Main functions:
- `opendev` opens an endpoint directory’s `ctl` file and builds a `Dev`.
- `opendevdata` opens the endpoint `data` file.
- `openep` creates or opens an endpoint under `/dev/usb/ep<dev>.<id>`, sets max packet, transaction count, and polling interval.
- `loaddevdesc`, `loaddevconf`, and `configdev` retrieve and parse descriptors into `Usbdev`.
- `loaddevstr` decodes USB UTF-16LE string descriptors.
- `closedev` reference-counts and frees `Dev`, descriptor tree, strings, endpoints, configs, and driver aux state.
- `usbcmd` builds control transfer packets, retries failed commands, and handles request/response phases.
- `unstall` clears endpoint halt both at USB standard request level and kernel endpoint `ctl`.
- `devctl` writes a single formatted control command.

Important design:
- `Dev` has one existence reference plus per-I/O or per-driver references.
- Descriptor parsing is delegated to `parse.c`.
- Control transfer debugging uses `hexstr` and request formatting.

Risks/quirks:
- Some endpoint naming behavior is retained for backward compatibility.
- `usbcmd` only treats positive counts as success, so zero-length replies are special-cased by callers.
