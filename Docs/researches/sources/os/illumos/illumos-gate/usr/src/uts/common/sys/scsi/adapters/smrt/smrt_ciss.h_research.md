# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/scsi/adapters/smrt/smrt_ciss.h

This header defines CISS transport constants and packed controller command/data structures for the `smrt` driver.

Key definitions:
- Defines CISS limits: `CISS_MAXSGENTRIES`, fallback scatter/gather count, and fixed 16-byte CDB length.
- Defines CISS command completion status values, transfer direction values, request attributes, and request type values.
- Defines I2O register offsets used by Smart Array controllers, including inbound/outbound post queues, interrupt registers, scratchpad, and configuration table offsets.
- Defines interrupt, doorbell, scratchpad, configuration table, and simple transport helper macros.
- `smrt_tag_t` models completion tags with reserved/error/tag-value fields.
- `SCSI3Addr_t`, `PhysDevAddr_t`, `LogDevAddr_t`, and `LUNAddr_t` model the controller’s LUN address encodings.
- `CommandList_t` is the packed controller command block with header, request block, error descriptor, and static scatter/gather descriptor array.
- `ErrorInfo_t` and `MoreErrInfo_t` describe controller error completions and embedded sense data.
- `CfgTable_t` describes the controller configuration table used to negotiate transport mode and discover controller limits.

Dependencies:
- Uses `MAX_SENSE_LENGTH`, supplied by SCSI implementation sense definitions through the broader include graph.
- Consumed directly by `smrt.h` and `smrt_scsi.h`.

Impact:
- This is a hardware ABI header. Structure layout, packing, field widths, and register constants must match controller firmware behavior.

Cautions:
- The file uses `#pragma pack(1)` around wire structures.
- Several structures contain C bitfields mapped to device-defined byte layouts, so compiler and endian assumptions matter.
- The controller command list statically allocates 64 scatter/gather entries for every command, influencing memory footprint.
