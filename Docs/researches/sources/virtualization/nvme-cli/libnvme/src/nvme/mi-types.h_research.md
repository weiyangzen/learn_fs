# File Research: sources/virtualization/nvme-cli/libnvme/src/nvme/mi-types.h

NVMe-MI wire protocol type definitions.

Key definitions:
- `NVME_MI_MSGTYPE_NVME` (`0x84`), the MCTP NVMe message type with MIC bit set.
- MI message type enum:
  - control primitive
  - MI command
  - Admin command
  - PCIe command
  - asynchronous event
- Request/response direction enum.
- MI response status enum with standard NVMe-MI status codes.
- Packed wire structs:
  - generic MI message header
  - generic response
  - MI request/response headers
  - Admin request/response headers
  - Control request/response structs
- MI command opcode enum for Read MI Data, Health Status Poll, Configuration Set/Get.
- Data Structure Type enum for subsystem, port, controller list, controller info, optional command support, and MEB support.
- Configuration IDs and SMBus frequency values.
- Asynchronous Event Message structures:
  - supported list header/item
  - enable list header/item
  - occurrence data
  - occurrence list header
  - full AEM message header
- Declares bitfield helper functions for AEM supported/enabled/event occurrence fields.

Research notes:
- The file is protocol/wire-layout focused, separate from higher-level NVMe-MI payload structures in `nvme-types-mi.h`.
- Packed attributes and explicit endian types are essential because these structures map directly to MI/MCTP payloads.
