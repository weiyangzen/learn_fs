# File Research: sources/os/plan9/plan9/sys/src/9/pc/usbuhci.c

Plan 9 kernel driver for USB Universal Host Controller Interface controllers. It registers `"uhci"` through `usbuhcilink()` and supplies the generic USB HCI callbacks for PCI discovery, frame-list setup, endpoint lifecycle, TD/QH I/O, interrupt processing, root-port operations, debugging, and shutdown.

Core structures:
- `Ctlr` owns I/O port base, dummy queue heads by transfer type, active QH list, active iso list, UHCI frame list, load counters, and interrupt counters.
- `Qh` mirrors UHCI queue-head hardware words plus software state and TD list.
- `Td` mirrors UHCI transfer descriptors and includes small embedded data storage plus optional allocated buffer.
- `Qio`, `Ctlio`, and `Isoio` track per-endpoint transfer state, toggles, cached control data, and ring-like isochronous TD state.
- Global `tdpool` and `qhpool` allocate aligned TD/QH chunks.

Transfer model:
- `uhcimeminit()` builds dummy QHs for control, interrupt, bulk, plus a loopback BWS workaround TD, then installs the frame list.
- Non-iso I/O uses `epio()` to build max-packet-sized TD chains, set active/IOC bits, link them into a QH, wait in `epiowait()`, collect data and toggles, then free TDs.
- Control I/O in `epctlio()` performs setup, data, and status phases and caches device-to-host response data for `epread()`.
- Bulk writes are chunked to `Tdatomic * ep->maxpkt` to avoid babble errors.
- Interrupt I/O rate-limits polling by `ep->pollival`.
- Isochronous I/O supports both half-duplex input and output. `isoopen()` installs periodic TDs in the frame list, `episoread()` drains completed IN TDs, and `episowrite()` fills OUT TDs.

Interrupt path:
- `interrupt()` acknowledges UHCI status, checks controller run state, then scans all active iso streams and all QHs because UHCI completion does not identify the source.
- `qhinterrupt()` walks software TD chains, handles NAK retry, fatal errors, short packets, and marks QHs done.
- `isointerrupt()` processes a bounded number of completed frames, tracks consecutive errors, advances user/hardware TD pointers, and wakes readers/writers.

Port/controller operations:
- `scanpci()` finds USB class/subclass controllers with programming interface `0`, allocates I/O space from BAR4, and stores PCI devices.
- `reset()` honors `*nousbuhci`, claims a controller, fills `Hci` callbacks, sets default `nports = 2`, and calls `uhcireset()` and `uhcimeminit()`.
- `init()` enables UHCI interrupts, starts the controller, and probes extra ports by reading port status registers.
- `portenable()`, `portreset()`, and `portstatus()` wrap UHCI port status/control bits into generic hub semantics.

Notable risks and comments:
- Header BUGS mention excessive delays/locks, per-frame bandwidth admission not implemented, interrupt endpoints not on an OHCI/EHCI-like tree, and missing power-overrun warnings.
- Isochronous bandwidth only prints a warning when load may exceed 800; it does not reject the endpoint.
- `portstatus()` has a `waserror()` cleanup path that calls `iunlock(ctlr)` even though the lock may not be held if `qlock()` faults, matching old Plan 9 idioms but worth care.
