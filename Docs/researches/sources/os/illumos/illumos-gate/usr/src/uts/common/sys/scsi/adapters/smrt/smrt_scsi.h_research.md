# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/scsi/adapters/smrt/smrt_scsi.h

This header defines Smart Array vendor-specific SCSI, CISS message, BMIC command, discovery, physical drive, and async event payload structures.

Key definitions:
- Defines CISS LUN addressing mode constants for physical devices and logical volumes.
- Defines vendor-specific CISS SCSI opcodes for read/write and reporting logical or physical LUNs.
- Defines BMIC read/write opcodes and Smart Array BMIC command IDs for identifying controllers, identifying physical devices, and event notification.
- Defines device/PHY type codes for pSCSI, SATA, SAS, expander, SES, controller, SGPIO, NVMe, and no-phy cases.
- Packed request/response structures cover:
  - `REPORT LOGICAL LUNS`
  - `REPORT PHYSICAL LUNS`
  - physical extended data variants for physical node identifiers and other physical device info
  - `IDENTIFY CONTROLLER`
  - `IDENTIFY PHYSICAL DEVICE`
  - CISS event notification request/response records
- Defines event classes/subclasses for protocol errors, hotplug, hardware/environment events, physical device state, and logical volumes.

Dependencies:
- Includes `smrt_ciss.h` for `LogDevAddr_t`, `PhysDevAddr_t`, and `LUNAddr_t`.
- Requires `SMRT_MAX_LOGDRV` and `SMRT_MAX_PHYSDEV`, which are defined by `smrt.h` before this header is included in the normal driver include path.

Impact:
- This is the driver’s command payload catalog for Smart Array firmware management commands.
- Discovery, event handling, physical device support, and SATA/SAS identification depend on these structures.

Cautions:
- Several multi-byte fields are explicitly noted as big-endian inside otherwise packed controller payloads.
- `smrt_identify_physical_drive_t` is large and firmware-version-sensitive; not every field is valid for every controller generation.
- Event notification requires a 512-byte buffer even though the exposed structure is shorter.
