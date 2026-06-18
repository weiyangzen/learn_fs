# File Research: sources/windows/windows-driver-samples/filesys/miniFilter/avscan/filter/scan.h

Kernel-private scan interface header. It defines scan mode and declares the scan entry points used by the main minifilter.

Key definitions:
- `AV_SCAN_MODE`: `AvKernelMode` and `AvUserMode`.

Declared interfaces:
- `AvScanInKernel`: performs scan using a kernel-created data-scan section and kernel memory search.
- `AvScanInUser`: coordinates user-mode scanner work through Filter Manager messaging.
- `AvCreateSectionForDataScan`: declared but not implemented in the listed `scan.c`; section creation is implemented through `FltCreateSectionForDataScan` in `scan.c` and `communication.c`.
- `AvCloseSectionForDataScan`: wraps section close/cleanup.

Dependencies:
- Includes `avlib.h` and relies on Filter Manager and AV context types included before or through `avscan.h`.

Research notes:
- The exposed abstraction is small: callers choose kernel/user scan and section lifecycle helpers stay hidden behind this interface.
