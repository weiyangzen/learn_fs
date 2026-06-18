# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/fm/io/ddi.h

This header defines DDI/device-driver Fault Management Architecture class and payload strings for I/O and driver defect reporting.

Primary constants:
- `DDI_DVR_MAX_CLASS` is 32.
- `DDI_IO_CLASS` is `"io"`.

Device ereport classes:
- Generic device errors include invalid state, no response, stall, bad interrupt limit, internal correctable/uncorrectable errors, firmware corrupt, and firmware mismatch.
- Service impact classes include lost, degraded, restored, and unaffected.
- Generic NIC event support includes `DDI_FM_NIC`, `DDI_FM_TXR_ERROR`, and valid TX ring error values such as whitelist, not supported, over temperature, hardware failure, and unknown.

Driver defect reporting:
- Driver defect prefix is `DVR_ERPT` (`"ddi."`).
- Defect suffixes describe invalid context, invalid semantics, bad FM capability, and invalid structure version.
- Payload fields include driver name, stack, stack depth, and driver-specific error data.

Dependencies and relationships:
- This is a naming-contract header for FMA nvlist producers and consumers.
- Driver code can include it to emit class/payload names without hard-coded strings.
