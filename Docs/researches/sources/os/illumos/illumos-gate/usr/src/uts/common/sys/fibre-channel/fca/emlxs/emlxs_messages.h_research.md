# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/fibre-channel/fca/emlxs/emlxs_messages.h

## Purpose

Defines the driver’s message catalog and message metadata generation macros. The same header can emit extern declarations, concrete `emlxs_msg_t` objects, or a report table depending on preprocessor mode.

## Main Definitions

### Generation Modes

`DEFINE_MSG` expands differently under:

- `DEF_MSG_REPORT`: emits report entries and also includes description/action fields.
- `DEF_MSG_STRUCT`: defines `emlxs_msg_t` variables.
- default mode: declares `extern emlxs_msg_t` variables.

This lets the driver maintain one catalog while generating declarations, definitions, and documentation/report data.

### Message Groups and Masks

Defines group ranges:

- Miscellaneous: 000-099
- Driver: 100-199
- Initialization: 200-299
- Memory: 300-399
- SLI: 400-499
- Mailbox: 500-599
- Node: 600-699
- Link: 700-799
- ELS: 800-899
- Packet: 900-999
- FCP: 1000-1099
- FCT target mode: 1100-1199
- IP: 1200-1299
- SFS: 1300-1399
- IOCTL: 1400-1499
- Firmware: 1500-1599
- CT: 1600-1699
- FC-SP/DHCHAP: 1700-1799
- FCF: 1800-1899

Defines verbose masks such as `MSG_DRIVER`, `MSG_INIT`, `MSG_MEM`, `MSG_SLI`, `MSG_MBOX`, `MSG_NODE`, `MSG_LINK`, `MSG_ELS`, `MSG_PKT`, `MSG_FCP`, `MSG_FCT`, `MSG_IOCTL`, `MSG_FIRMWARE`, `MSG_CT`, `MSG_FCSP`, `MSG_FCF`, and detail masks including `MSG_MBOX_DETAIL` and `MSG_SLI_DETAIL`.

Defines levels: `EMLXS_DEBUG`, `EMLXS_NOTICE`, `EMLXS_WARNING`, `EMLXS_ERROR`, and `EMLXS_PANIC`.

### Message Type

`emlxs_msg_t` contains:

- fixed message buffer/name string
- numeric id
- level
- mask
- optional report description/action/flags under `DEF_MSG_REPORT`
- FMA ereport code pointer
- FMA impact code

### Catalog Content

The file contains the full catalog of driver messages, with entries for attach/detach/suspend/resume, initialization, memory pools, SLI/link state, mailbox completion/errors, node state, ELS send/receive/rejects, packet/FCP/IP/CT completions, diagnostics, firmware download/update/dump events, IOCTL/DFC traces, optional SFCT target-mode messages, optional DHCHAP/FC-SP messages, and FCF messages.

Several entries include FMA ereport and service-impact codes such as `DDI_FM_DEVICE_INVAL_STATE`, `DDI_FM_DEVICE_INTERN_UNCORR`, `DDI_FM_DEVICE_INTERN_CORR`, `DDI_SERVICE_LOST`, `DDI_SERVICE_DEGRADED`, and `DDI_SERVICE_UNAFFECTED`.

## Integration Notes

This header is included by `emlxs_msg.h` and by at least one compilation unit with `DEF_MSG_STRUCT` to instantiate the catalog. It relies on `emlxs_msg_t` being valid in the chosen expansion context.

Optional message entries are gated by feature macros such as `SFCT_SUPPORT` and `DHCHAP_SUPPORT`, so the available symbol set depends on build configuration.

## Risks and Gotchas

- Because the same header changes meaning based on macros, include order and one-definition discipline matter.
- FMA code constants must be available where catalog definitions are emitted.
- Message ids are grouped but not mechanically enforced by the type system.
- The catalog mixes operational logs and service-action/report text; changing strings can affect both driver diagnostics and generated reports.
