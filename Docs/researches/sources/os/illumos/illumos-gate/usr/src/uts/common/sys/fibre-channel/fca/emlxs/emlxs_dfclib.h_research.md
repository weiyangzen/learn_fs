# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/fibre-channel/fca/emlxs/emlxs_dfclib.h

## Purpose

`emlxs_dfclib.h` defines the shared DFC library/driver data structures and constants for board discovery, mailbox commands, firmware/config access, CT vendor commands, NPIV, DH-CHAP management, FCP command/response layout, and FCoE information.

## Main Types

Board discovery types include `brdinfo_t` and `dfc_brdinfo_t`.

DMA/buffer descriptors include `ulp_bde_t` and `ulp_bde64_t`.

Mailbox command payloads include read service parameters, read revision, dump, dump4, update config, SLI config, read config, read log, log status, read event log, `dfc_mailbox_t`, and `dfc_mailbox4_t`.

FCoE config-region records include `tlv_fcoe_t`, `tlv_fcfconnectentry_t`, and `tlv_fcfconnectlist_t`.

Information structures include `dfc_ioinfo_t`, `dfc_linkinfo_t`, `dfc_traceinfo_t`, `dfc_cfgparam_t`, `dfc_nodeinfo_t`, `dfc_vpd_t`, `dfc_destid_t`, `dfc_loopback_t`, `dfc_drvinfo_t`, `dfc_regevent_t`, binding-list structures, CT request structures, NPIV virtual port/resource/link/node structures, DH-CHAP config/password/status structures, FCP command/response structures, send-SCSI/FCP command info, and FCoE FCF list structures.

## Constants

Mailbox command codes cover shutdown, firmware load/run, NVRAM, diagnostics, link init/down/config, ring config/reset, read config/status/revision/link, login/unlogin, dump, update/download, MSI, SLI config, RPI/VFI/FCFI/VPI operations, and feature requests.

Event masks cover link, RSCN, CT, multipulse, dump, temperature, vport RSCN, SAN diagnostic events, and FCoE events.

Capability masks distinguish online/offline diagnostic operations, endian mode, SLI support, memory/flash/PCI/control-register access, configuration support, CT, HBA API, and SBUS.

Vendor-unique CT opcodes cover adapter/server/HBA/port/driver attributes, statistics, firmware verification/download/upgrade, HBA reset/diagnostics, security/access/key tables, SCSI target mapping and report-luns/inquiry/read-capacity, persistent binding, node/address discovery, loopmap, beacon, and PCI register access.

NPIV constants define result codes, vport states, options, readiness checklist bits, and vport attributes.

FCP constants define SCSI status, FCP response validity/residual bits, task attributes, task management bits, and read/write flags.

## Research Notes

This is the largest DFC ABI header and contains many wire/hardware layouts with endian-dependent bitfields. It connects userland management tools, driver ioctl handling, mailbox firmware commands, FC protocol operations, NPIV, FCoE, and FCP/SCSI data paths.
