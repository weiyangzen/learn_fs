# File Research: sources/os/plan9/plan9/sys/src/cmd/usb/serial/ftdi.c

FTDI backend for the generic USB serial driver.

Major components:
- Large `ftinfo[]` VID/DID table for FTDI and FTDI-based products.
- `ftdiread`/`ftdiwrite` wrap FTDI vendor/class control requests.
- Baud divisor calculation supports SIO, AM, BM, 2232/4232-style devices, plus special divisor quirks.
- `ftgettype` infers chip family, interface count, packet size, baud base, input/output header sizes, and optional JTAG interface.
- `ftsetparam`, `ftmodemctl`, `ftsendlines`, and `ftsetbreak` implement serial line configuration.
- `ftuseinhdr` consumes FTDI input status headers and updates modem/error counters.
- `wait4data` and `wait4write` integrate FTDI packet headers with the common serial read/write layer.
- Background `epreader` reads endpoint data, strips FTDI status headers with `cpdata`, and sends buffered packets to `statusreader`.
- `statusreader` coordinates common-layer blocking reads through `w4data`/`gotdata`.
- `ftinit` starts status reading and, for JTAG, configures latency, timeouts, and MPSSE bit mode.
- `ftreset` and `ftclearpipes` issue FTDI reset/purge commands.

Notable quirks:
- FTDI input packets carry two status bytes per USB packet and optional output headers for old SIO devices.
- Multi-interface devices can expose a JTAG interface named separately by the common layer.
- The `ftdiwrite` request test uses `||`, making the index adjustment effectively always applied.
