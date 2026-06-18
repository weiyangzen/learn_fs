# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/fibre-channel/fca/emlxs/emlxs_hw.h

Purpose: Defines low-level Emulex adapter hardware, SLI, Fibre Channel, FCP/SCSI, ELS, CT, FDMI, buffer descriptor, DMA map, and firmware-image constants and structures.

Key definitions:
- Adapter capacity and ring constants: max vports, max transfer, ring counts, PCB size, SLI2/SLI3 IOCB sizes, SLIM sizes, command/ring assignments for FCP/FCT/IP/ELS/CT, retry and timeout defaults.
- Well-known D_ID values: FDMI, name server, SCR, fabric, broadcast, Menlo, and masks.
- FC frame R_CTL/type constants and command/response direction flags.
- CT structures: `CtRevisionId_t`, `CtCommandResponse_t`, `SliCtRequest_t`; CT service types, name-server subtype, accept/reject codes, reason/explanation codes, management-server and name-server command IDs, port types, and last-entry flag.
- PCI/SBUS register offsets and bit masks: BARs, command/status, capabilities, extended capabilities, configuration access, SBUS control/status/update, host/chip attention/status/control, BIU config.
- MSI maps/masks and interrupt mode definitions under `MSI_SUPPORT`.
- SLI4 register offsets and bit definitions: UE status/mask registers, EQ interrupt CSR registers, SLI status/control, physical-device control, POST/semaphore fields, BAR doorbells, MQ/CQ/EQ/WQ doorbell bit layouts, bootstrap mailbox constants.
- FCP/SCSI payloads: `FCP_RSP`, `FCP_CMND`, inquiry data, read capacity, SCSI status/response codes, CDB opcodes, and vendor-specific CDB values.
- Fibre Channel service parameter structures: rings, ring definitions, `NAME_TYPE`, common service parameters, class parameters, `SERV_PARM`, vendor version format, and endian-sensitive bitfields.
- ELS constants and payloads: command codes for LS_RJT, ACC, PLOGI/FLOGI/LOGO/PRLI/PRLO/ADISC/FARP/FAN/RSCN/SCR/RNID/AUTH and more; payload structs for LS_RJT, LOGO, PRLI, PRLO, ADISC, FARP, FAN, SCR, RNID, RRQ, D_ID, and aggregate `ELS_PKT`.
- Buffer/DMA descriptors: `ULP_BDE`, `ULP_BDE64`, `ULP_BPL64`, `ULP_BDL`, `ULP_SGE64`, `BE_PHYS_ADDR`, and `MATCHMAP`.
- FDMI/HBA management definitions: operation codes, subtype, reject code, HBA/port attribute types, attribute entries/blocks, port/HBA identifiers, registration payloads, and accept payloads.
- Firmware/download definitions: SRAM config constants, SLI firmware adapter type encodings, program type enum, firmware image/file descriptors, checksum/AIF/flash/load-list constants, object max transfer, BE2/BE3 UFI/flash directory structures, flash entry types, driver-level BE firmware file/image structures, and object firmware header.

Dependencies and interactions:
- Provides foundational hardware/protocol types consumed by `emlxs_fc.h`, `emlxs_fcf.h`, firmware download code, mailbox code, ELS/CT/FCP paths, and dump code.
- Requires endian macros (`EMLXS_BIG_ENDIAN`, `EMLXS_LITTLE_ENDIAN`) to choose protocol bitfield layout.
- References constants defined elsewhere, such as `MBOX_SIZE`, `MBOX_EXTENSION_SIZE`, `MBOX_EXTENSION_OFFSET`, and `RQ_DEPTH`.

Implementation notes:
- This file is declarative and ABI/protocol-layout heavy; bitfield ordering and structure sizes are hardware/protocol sensitive.
- Several variable-length payload structures are represented with single-element trailing arrays, a pre-C99 idiom used throughout this driver.
- It includes both older FireFly/SLI2/SLI3 register definitions and newer SLI4/BladeEngine firmware formats, showing support across adapter generations.
