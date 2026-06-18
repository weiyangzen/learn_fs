# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/nxge/nxge_common.h

## Purpose

`nxge/nxge_common.h` defines common Neptune/NIU DMA, classification, partition, and hardware-resource configuration structures shared by nxge driver components.

## Main Interfaces

The header defines default per-port RX/TX DMA channel counts for NIU and Neptune, RDC group counts, timer constants, and descriptor/ring sizing defaults. Several defaults vary by platform, endian, architecture, and NIU workaround macros.

`nxge_rdc_cfg_t` describes a receive DMA channel: partitioning/logical-page setup, WRED parameters, mailbox address, header mode, buffer offsets and block sizes, RBR/RCR addresses and lengths, completion thresholds/timeouts, logical-device group, event masks, and address mode.

`nxge_tdc_cfg_t` describes a transmit DMA channel: partitioning/logical-page setup, transmit ring address/length, mailbox, logical-device group, event mask, reclaim threshold, packet counter, and last mark.

`nxge_tdc_grp_t` and `nxge_rdc_grp_t` describe transmit and receive DMA channel groups, including start channel, max count, bitmap, default RDC, config method, and logical group index. Bit macros manipulate RDC/DC maps.

`nxge_dma_pt_cfg_t` is per-port DMA configuration: MAC port, hardware properties, buffer/ring sizes, TX map, TDC/RDC groups, per-RDC interrupt thresholds/timeouts, full-header flag, and RX DRR weight.

`nxge_class_pt_cfg_t` configures MAC/VLAN classification tables, hash initializers, multicast/default group mapping, and TCAM class config values.

`nxge_common_t` stores per-device shared common resources such as partition id, 32-bit mode, all RDC/TDC configs, DMA common config, timer resolution, system-error owner, layer 2/3/4 classifier EtherTypes, and hash initial values.

`nxge_part_cfg_t` models partition/logical-domain configuration: RDC/TDC maps, per-port configs, flow classification partitioning, and service/read-write/read-only attributes.

`nxge_hw_list_t` is the per-hardware shared state object containing locks, parent device pointer, per-function `nxge_t` pointers, device count, flags, hardware/platform type, transceiver addresses, HIO/TCAM pointers, TCAM size, and programmable L2/L3 class tracking.

## Runtime Use

Driver initialization reads platform/firmware properties into these structures, allocates DMA resources, configures hardware rings/groups, partitions resources across ports or domains, and uses classification maps to steer traffic to RDC groups.

## Dependencies

The header relies on many constants and types from nxge hardware, DMA, classifier, and platform headers included before it by nxge components.

## Risks and Invariants

Ring size defaults are highly conditional. Changing macros can alter DMA memory footprint and hardware programming on specific platforms.

The bitfield structures `nxge_param_map_t` and `nxge_rcr_param_t` have separate big- and little-endian layouts; serialized or register-facing use must preserve endian semantics.

Resource maps and group indexes must stay within hardware maxima. Incorrect partition maps can assign the same DMA channel or classification resource to multiple owners.
