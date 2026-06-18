# File Research: sources/virtualization/nvme-cli/libnvme/src/meson.build

This Meson file defines the libnvme C library sources, headers, link scripts, dependencies, and installed headers.

Core source selection:
- Always includes core accessors, base64, crc32, ioctl, log, command, and util sources.
- On Windows, uses Windows ioctl/memory/no-crypto sources.
- Otherwise includes crypto, filters, Linux ioctl/lib/sysfs/tree/memory support.
- If `want_fabrics`, adds fabrics, NBFT, tree-fabrics, util-fabrics, and accessors-fabrics sources/headers.
- If no fabrics, adds `no-fabrics.c`.
- If `want_mi`, adds MI and MCTP sources/headers; otherwise `no-mi.c`.
- If liburing is available, adds `uring.c`; otherwise `no-uring.c`.
- If json-c and fabrics are available, adds `json.c`; otherwise `no-json.c`.

Build outputs:
- Configures `libnvme.h` from `libnvme.h.in`, including fabrics headers conditionally.
- Builds shared library with hidden visibility and version scripts.
- Generates pkg-config metadata.
- Declares `libnvme_dep`.
- Builds `libnvme-test` without version scripts for MI unit tests.
- Installs headers under `nvme`, plus `libnvme-mi.h` when MI is enabled.

Integration role:
- Central source and ABI definition for the libnvme library.
