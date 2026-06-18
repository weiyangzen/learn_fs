# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/fibre-channel/fca/emlxs/emlxs_mbox.h

## Purpose

Defines the mailbox command ABI for Emulex adapters across SLI2/3 and SLI4. This is the largest protocol header in the group: it includes mailbox command/status constants, per-command payload layouts, SLI port control blocks, SLI4 IOCTL mailbox requests, queue creation contexts, FCoE/FCF management records, and firmware download/load-list structures.

## Main Definition Areas

### Mailbox Commands and Status

Defines `MBX_*` opcodes from basic lifecycle commands (`MBX_INIT_LINK`, `MBX_DOWN_LINK`, `MBX_CONFIG_LINK`) through discovery/status (`MBX_READ_CONFIG`, `MBX_READ_REV`, `MBX_READ_LA`), login/resource management (`MBX_REG_LOGIN`, `MBX_UNREG_RPI`, `MBX_REG_VPI`, `MBX_REG_VFI`, `MBX_REG_FCFI`), diagnostics, firmware loading, event logging, and SLI4 `MBX_SLI_CONFIG`.

Status constants include firmware/adapter errors (`MBXERR_*`) and driver-side pseudo-statuses (`MBX_BUSY`, `MBX_TIMEOUT`, `MBX_NOT_FINISHED`, `MBX_HARDWARE_ERROR`). Issue modes include `MBX_POLL`, `MBX_SLEEP`, `MBX_WAIT`, `MBX_NOWAIT`, and `MBX_BOOTSTRAP`.

### SLI2/3 Mailbox Payloads

Defines many mailbox payload structs, including:

- Firmware/program identity and compatibility: `REVCOMPAT`, `PROG_ID`, `LOAD_SM_VAR`, `LOAD_AREA_VAR`, `LOAD_EXP_ROM_VAR`.
- Link configuration and status: `INIT_LINK_VAR`, `CONFIG_LINK`, `READ_CONFIG_VAR`, `READ_CONFIG4_VAR`, `READ_LNK_VAR`, `READ_LA_VAR`, `CLEAR_LA_VAR`.
- Ring and HBQ configuration: `PART_SLIM_VAR`, `CONFIG_RING_VAR`, `READ_RCONF_VAR`, `HBQE_t`, `HBQ_INIT_t`, `CONFIG_HBQ_VAR`.
- Service parameters and login state: `READ_SPARM_VAR`, `READ_RPI_VAR`, `READ_XRI_VAR`, `REG_LOGIN_VAR`, `UNREG_LOGIN_VAR`, `REG_WD30`.
- NPIV/FCoE fabric identity: `REG_VPI_VAR`, `INIT_VPI_VAR`, `UNREG_VPI_VAR`, `UNREG_VPI_VAR4`, `REG_VFI_VAR`, `INIT_VFI_VAR`, `UNREG_VFI_VAR`, `REG_FCFI_VAR`, `UNREG_FCFI_VAR`, `RESUME_RPI_VAR`.
- Diagnostics and dumps: `BIU_DIAG_VAR`, `DUMP_VAR`, `DUMP4_VAR`, `READ_EVT_LOG_VAR`, `LOG_STATUS_VAR`.
- Port/config feature negotiation: `CONFIG_PORT_VAR`, `REQUEST_FEATURES_VAR`.

`MAILVARIANTS` is the union for SLI2/3 mailbox command overlays, and `MAILBOX` is the 256-byte volatile mailbox format including status/command/owner fields plus SLI pointer state.

### SLI4 IOCTL Mailbox Layer

Defines the SLI4 management request envelope:

- `mbox_req_hdr_t`
- `mbox_req_hdr2_t`
- `mbox_rsp_hdr_t`
- `be_req_hdr_t`
- `SLI_CONFIG_VAR`
- `MAILVARIANTS4`
- `MAILBOX4`

The IOCTL layer defines subsystem and opcode constants for common, low-level, FCoE, and DCBX operations. It includes flash operations, object read/write/list/delete, boot config, firmware config query, physical link config, extents, SLI4 parameters, queue creation, FCF table management, and DCBX mode get/set.

### Queue Creation Contexts

The file declares SLI4 queue context structures used by mailbox create commands:

- `EQ_CONTEXT`
- `CQ_CONTEXT`
- `CQ_CONTEXT_V2`
- `MQ_CONTEXT`
- `MQ_CONTEXT_V1`
- `RQ_CONTEXT`
- `RQ_CONTEXT_V1`

Associated request wrappers include `IOCTL_COMMON_EQ_CREATE`, `IOCTL_COMMON_CQ_CREATE`, `IOCTL_COMMON_CQ_CREATE_V2`, `IOCTL_COMMON_MQ_CREATE`, `IOCTL_COMMON_MQ_CREATE_EXT`, `IOCTL_COMMON_MQ_CREATE_EXT_V1`, `IOCTL_FCOE_RQ_CREATE`, `IOCTL_FCOE_RQ_CREATE_V1`, `IOCTL_FCOE_WQ_CREATE`, and `IOCTL_FCOE_WQ_CREATE_V1`.

### FCoE and Management Structures

Defines FCoE/FCF management records and operations:

- `FCF_RECORD_t`
- `IOCTL_FCOE_READ_FCF_TABLE`
- `IOCTL_FCOE_ADD_FCF_TABLE`
- `IOCTL_FCOE_DELETE_FCF_TABLE`
- `IOCTL_FCOE_REDISCOVER_FCF_TABLE`
- `IOCTL_FCOE_CFG_POST_SGL_PAGES`
- `IOCTL_FCOE_POST_HDR_TEMPLATES`
- `MGMT_HBA_ATTRIB`
- `MGMT_CONTROLLER_ATTRIB`
- `IOCTL_COMMON_GET_CNTL_ATTRIB`

### Firmware Image and Flash Layout

At the end, the file defines flash/download constants, image addresses, `AIF_HDR`, `IMAGE_HDR`, `WAKE_UP_PARMS`, `LOAD_ENTRY`, and `LOAD_LIST`. These model firmware area IDs, erase/download/copy state machines, and load-list entries.

## Integration Notes

This header is central to adapter bring-up, firmware management, mailbox command submission, SLI4 queue setup, FCoE discovery, and NPIV/fabric resource management. It depends on many driver and Fibre Channel types defined elsewhere, including `ULP_BDE`, `ULP_BDE64`, `MATCHMAP`, `BE_PHYS_ADDR`, `NAME_TYPE`, `emlxs_ring_def_t`, `emlxs_rings_t`, `MAX_RINGS_AVAILABLE`, `SLI_SLIM1_SIZE`, `SLI_IOCB_MAX_SIZE`, and related SLI definitions.

`emlxs_mbq_t` is the software mailbox queue wrapper. It stores the raw mailbox words, queue linkage, deferred completion context pointers, flags, optional extension buffer, and completion callback.

## Risks and Gotchas

- This is an ABI header. Layout changes can break firmware/hardware communication.
- Endian-specific bitfields are pervasive and must remain synchronized.
- Several opcodes intentionally share numeric values across SLI generations, for example SLI2/3 `MBX_UNREG_LOGIN` and SLI4 `MBX_UNREG_RPI`.
- Many variable-length command shapes use one-element arrays or integer fields that represent trailing payloads or DMA buffers; bounds checking must live in command construction code.
- `MBOX_EXT_SUPPORT` changes mailbox extension sizing and `emlxs_mbq_t` fields.
- Some fields are comments-as-contract, such as page counts, object name word spans, and flash offsets; there is little type-level enforcement.
