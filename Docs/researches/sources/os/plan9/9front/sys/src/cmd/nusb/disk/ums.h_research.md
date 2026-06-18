# File Research: sources/os/plan9/9front/sys/src/cmd/nusb/disk/ums.h

This header defines USB mass-storage transport constants and data structures. It includes protocol/subclass ids, class-specific request codes (`Umsreset`, `Getmaxlun`), maximum LUN/partition limits, raw-command phase values, CBW/CSW sizes and status codes, and data direction flags.

`Part` represents a served partition in logical-block units. `Umsc` embeds `ScsiReq` as its first field and extends it with a served name, block count, byte capacity, transfer setup scratch state, a `QLock`, partition table, raw command buffer, raw phase, inquiry string, parent `Ums`, and an aligned I/O buffer sized to `Maxiosize`.

`Ums` stores the opened USB IN/OUT endpoints, the LUN array, maximum LUN index, bulk-only sequence tag, and a quirk flag for devices that report wrong residues.

`Cbw` and `Csw` model the USB bulk-only Command Block Wrapper and Command Status Wrapper layouts used by `disk.c`'s `umsrequest()`.
