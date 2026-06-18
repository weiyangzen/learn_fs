# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/nxge/nxge_fflp.h

## Purpose
Defines software state, statistics, and configuration constants for the Fast Frame Lookup Processor: VLAN/RDC mapping, TCAM flow entries, FCRAM hash-cell occupancy, programmable classification keys, and FFLP error accounting.

## Main Interfaces
- Error/stat structures:
  - `fflp_errlog_t`
  - `nxge_fflp_stats_t`
- FCRAM occupancy constants for empty, IPv4 exact, IPv6 exact, optimistic, and mixed cell layouts.
- `fcram_cell_t`: tracks cell type, occupied subareas, and shadow location.
- `fcram_parition_t`: describes a hash partition with id/base/mask/relocation/flags/offset/size.
- `tcam_flow_spec_t`: TCAM entry plus flags, user metadata, and validity.
- Classification config flags such as `NXGE_CLASS_TCAM_LOOKUP`, `NXGE_CLASS_FLOW_USE_IPSRC`, `NXGE_CLASS_FLOW_USE_IPDST`, `NXGE_CLASS_FLOW_USE_SRC_PORT`, `NXGE_CLASS_FLOW_USE_DST_PORT`, and `NXGE_CLASS_DISCARD`.
- `vlan_rdcgrp_map_t`: VLAN-to-RDC-group mapping.
- `nxge_classify_t`: central software classification state containing locks, TCAM entries, programmable class state, flow keys, FCRAM hash table, per-partition state, and fragment-bug tracking.

## Dependencies And Relationships
Includes `npi_fflp.h` and uses `tcam_entry_t` from the FFLP hardware definitions. The state is initialized and manipulated by the classify/FFLP routines prototyped in `nxge_impl.h`.

## Research Notes
The file documents FCRAM cell packing rules in detail. There is a likely legacy typo: `FCRAM_SUBAREA7_OCCUPIED` is defined as `0x20`, duplicating subarea 5 instead of using a distinct bit.
