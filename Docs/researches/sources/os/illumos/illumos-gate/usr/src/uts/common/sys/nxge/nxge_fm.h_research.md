# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/nxge/nxge_fm.h

## Purpose
Defines NXGE Fault Management Architecture ereport names, block identifiers, ereport IDs, and attribute metadata used to report hardware and software faults.

## Main Interfaces
- Ereport attribute name strings for detailed error type, port/channel numbers, TCAM/VLAN/hash logs, RDMC/TDMC logs, IPP/ZCP state, FIFO entries, TXC ECC/reorder state, and related diagnostic fields.
- Ereport ID packing macros:
  - `EREPORT_FM_ID_SHIFT`
  - `EREPORT_FM_ID_MASK`
  - `EREPORT_INDEX_MASK`
- FM block IDs mapped from hardware block IDs, including MAC, MIF, IPP, TXC, TXDMA, RXDMA, ZCP, ESPC, FFLP, PCIE, VIR, XAUI, and XFP.
- `nxge_fm_ereport_id_t`
- `nxge_fm_ereport_attr_t`: index, display string, ereport class, and `ddi_fault_impact_t`.
- Ereport enums for PCS/MIF/FFLP/IPP/RDMC/ZCP/RXMAC/TDMC/TXC/TXMAC/ESPC/software/XAUI/XFP failures.

## Dependencies And Relationships
Includes `sys/ddi.h` for DDI fault impact types. `nxge_impl.h` declares `nxge_fm_report_error()` and external FMA handle-check helpers that consume these identifiers.

## Research Notes
This header is a taxonomy for fault reporting. The enum values are block-ID shifted, so consumers can recover the reporting hardware block from an ereport ID.
