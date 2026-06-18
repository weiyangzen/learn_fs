# File Research: sources/os/plan9/plan9/sys/src/cmd/usb/disk/ums.h

Read fully: 106 lines, 1787 bytes. SHA-256 prefix: `af10254364756eb2`.

This header defines USB mass-storage protocol/subclass constants, bulk-only transport constants, per-LUN/device structures, and CBW/CSW layouts.

`Umsc` embeds `ScsiReq` and adds capacity, setup state, raw command buffer, raw-phase state, inquiry string, parent `Ums`, per-LUN `Usbfs`, and an aligned transfer buffer. `Ums` tracks the USB device, bulk endpoints, LUN array, max LUN, sequence tag, error count, and residue quirk flag.

`Cbw` and `Csw` correspond to USB bulk-only Command Block Wrapper and Command Status Wrapper, using `"USBC"`/`"USBS"` signatures.

Integration: shared by `disk.c` and `main.c`; `diskmain()` is declared here for the device starter.

Risk notes: `Maxlun` is capped at 32 despite a commented 256. The structs assume transparent SCSI bulk-only transport and are not suitable for CBI/CB or ATA without new code.
