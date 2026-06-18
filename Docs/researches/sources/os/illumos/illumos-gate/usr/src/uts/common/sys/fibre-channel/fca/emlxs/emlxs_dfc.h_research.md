# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/fibre-channel/fca/emlxs/emlxs_dfc.h

## Purpose

`emlxs_dfc.h` defines the driver-facing DFC ioctl command envelope, command numbers, error codes, and high-level returned information structures for Emulex diagnostics/configuration/control.

## Main Types

`dfc_t` is the main command envelope: command, flag, and four buffer/data slots. `dfc32_t` is the 32-bit kernel-side ABI variant.

`sd_bucket_info_t` is conditionally defined for SAN diagnostics latency buckets.

`dfc_hbainfo_t` returns extensive HBA identity, VPD, firmware, driver, topology, port, supported type/speed, fabric, node count, and PCI location data.

`dfc_node_t` returns remote FC node identifiers, RPI/XRI, flags, and service parameters.

`dfc_hbastats_t` returns FC link and frame statistics.

`dfc_drvstats_t` returns driver counters for link, mailbox, IOCB, FCP, ELS, CT, IP, unsolicited buffers, and conditional DH-CHAP counters.

`dfc_tgtport_stat_t` is conditionally defined for target-mode I/O buckets and FCT counters.

`dfc_vportinfo_t` returns NPIV virtual port state, WWNs, symbolic names, and ULP state.

## Commands and Errors

Command numbers cover HBA, I/O, link, node, event, revision, dump region, HBA stats, driver stats, FCIO passthrough, config get/set, events, mailbox, ELS, CT, CT response, Menlo, SCSI, diagnostics, loopback, reset, PCI/flash/memory/control-register access, NPIV, DH-CHAP auth, target stats, persistent linkdown, FCoE FCF/DCBX/QoS, and SAN diagnostics.

Error codes start at `0x200` and distinguish system/driver/HBA/I/O errors, argument/copyin/copyout problems, timeouts, resource exhaustion, offline/online state, NPIV failures, auth failures, Menlo/linkdown cases, and SAN diagnostic errors.

## Research Notes

This is a privileged storage-adapter management ABI. It exposes low-level adapter operations, firmware/flash/register access, FC protocol passthrough, NPIV, authentication, FCoE, and diagnostic controls that can materially affect block-device availability.
