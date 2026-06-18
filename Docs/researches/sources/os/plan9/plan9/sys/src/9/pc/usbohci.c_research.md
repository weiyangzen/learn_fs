# File Research: sources/os/plan9/plan9/sys/src/9/pc/usbohci.c

Plan 9 kernel driver for USB Open Host Controller Interface controllers. It registers an `"ohci"` HCI type with the generic USB layer via `usbohcilink()` and implements controller discovery, reset, endpoint open/close, transfer submission, interrupt completion, root-hub port operations, and shutdown.

Key structures are hardware-descriptor mirrors plus software queues: `Ed` endpoint descriptors, `Td` transfer descriptors, `Hcca`, memory-mapped `Ohci` registers, `Qio` per-direction transfer state, `Ctlio`, `Isoio`, `Qtree` periodic schedule tree, descriptor pools, and `Ctlr`. Descriptor allocation uses global pooled `xspanalloc()` blocks with poisoning checks in `tdfree()`/`edfree()`.

Transfer model:
- Control and bulk endpoints are linked into OHCI control/bulk lists.
- Interrupt and isochronous endpoints are scheduled into a 32-entry periodic tree built by `mkqhtree()`.
- Non-iso I/O is driven by `epio()`, which builds TD chains from a dummy tail TD, starts hardware by updating the ED tail, waits through `epiowait()`, copies input data back, frees completed TDs, and preserves data toggles.
- Control requests are serialized by `epctlio()` into setup, data, and status phases; device-to-host data is cached for a later `epread()`.
- Isochronous output is supported through preallocated TD buffering in `isoopen()`, `putsamples()`, and `episowrite()`. Isochronous input explicitly panics/errors as not implemented.

Interrupt handling is in `interrupt()`: it drains the HCCA done queue, dispatches to `qhinterrupt()` or `isointerrupt()`, records transfer-type counters, reports scheduling overrun and unrecoverable error conditions, and re-enables selected interrupts. Error handling maps OHCI TD condition codes to Plan 9 error strings, with short IN packets treated as transfer termination rather than fatal errors.

Port and controller support:
- `scanpci()` finds USB class/subclass controllers with programming interface `0x10`, maps BAR0, and records PCI devices.
- `reset()` honors `*nousbohci`, claims an inactive controller, resets legacy support, initializes HCCA/periodic tree, and fills the `Hci` callback table.
- `init()`, `portreset()`, `portenable()`, and `portstatus()` program root-hub registers and translate OHCI port bits to generic hub status bits.
- `shutdown()` disables master interrupts and stops the controller.

Notable risks and comments:
- File header lists known issues: no isochronous input streams, too many delays/interrupt locks, incomplete bandwidth admission control, inefficient buffering, and missing power-overrun warning.
- `epgettd()` panics for transfers larger than two pages per TD and allocates page-aligned buffers for page-crossing cases.
- Many operations rely on `ilock()` around hardware list mutation and timed sleep after aborting TDs.
