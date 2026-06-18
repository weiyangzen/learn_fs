# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/pcie.h

## Purpose
Defines the public PCI Express register, capability, extended capability, AER, ARI, Device 3, TLP, requester ID, completion status, and link-training preset vocabulary.

## Main Interfaces
- PCIe capability register offsets:
  - `PCIE_PCIECAP`
  - `PCIE_DEVCAP`, `PCIE_DEVCTL`, `PCIE_DEVSTS`
  - `PCIE_LINKCAP`, `PCIE_LINKCTL`, `PCIE_LINKSTS`
  - `PCIE_SLOTCAP`, `PCIE_SLOTCTL`, `PCIE_SLOTSTS`
  - `PCIE_ROOTCTL`, `PCIE_ROOTCAP`, `PCIE_ROOTSTS`
  - `PCIE_DEVCAP2/DEVCTL2/DEVSTS2`
  - `PCIE_LINKCAP2/LINKCTL2/LINKSTS2`
  - `PCIE_SLOTCAP2/SLOTCTL2/SLOTSTS2`
- Config size:
  - `PCIE_CONF_HDR_SIZE`
- PCIe capability/device/link/slot/root bits:
  - `PCIE_PCIECAP_*`
  - `PCIE_DEVCAP*`
  - `PCIE_DEVCTL*`
  - `PCIE_DEVSTS*`
  - `PCIE_LINKCAP*`
  - `PCIE_LINKCTL*`
  - `PCIE_LINKSTS*`
  - `PCIE_SLOTCAP*`
  - `PCIE_SLOTCTL*`
  - `PCIE_SLOTSTS*`
  - `PCIE_ROOT*`
- Indicator helpers:
  - `pcie_slotctl_pwr_indicator_get()`
  - `pcie_slotctl_attn_indicator_get()`
  - `pcie_slotctl_attn_indicator_set()`
  - `pcie_slotctl_pwr_indicator_set()`
- Extended capability header and IDs:
  - `PCIE_EXT_CAP`
  - `PCIE_EXT_CAP_*`
  - `PCIE_EXT_CAP_ID_*` including AER, VC, serial number, ACS, ARI, ATS, SR-IOV, PASID, DPC, PTM, DOE, IDE, high-speed physical layer caps, SIOV, and captured data.
- AER offsets and bits:
  - `PCIE_AER_*`
  - uncorrectable/correctable/root/secondary error status, masks, severity, header logs, and source IDs.
- Serial Number and ARI capability offsets/bits.
- Device 3 extended capability:
  - `PCIE_DEVCAP3`
  - `PCIE_DEVCTL3`
  - `PCIE_DEVSTS3`
- TLP definitions:
  - TLP format/type constants
  - combined TLP encodings such as `PCIE_TLP_MRD3`, `PCIE_TLP_CFGWR0`, `PCIE_TLP_CPLD`, `PCIE_TLP_MSI64`
  - `pcie_tlp_hdr_t`
  - `pcie_mem64_t`
  - `pcie_memio32_t`
  - `pcie_cfg_t`
  - `pcie_cpl_t`
  - `pcie_msg_t`
- Requester/completer support:
  - `pcie_req_id_t`
  - `PCIE_REQ_ID_*`
  - `PCIE_CPL_STS_*`
- Message and equalization presets:
  - `PCIE_MSG_CODE_ERR_*`
  - `PCIE_GEN3_RX_PRESET_*`
  - `PCIE_TX_PRESET_*`

## Dependencies And Relationships
Includes `pci.h`, reusing base PCI capability offsets and IDs. Used by PCIe nexus drivers, error handling, link management, hotplug, and device drivers.

## Research Notes
The header is kept current with newer PCIe speeds and capabilities up through 64 GT/s and 128 GT/s identifiers. TLP structures are endian-conditional bitfields, so consumers must compile with `_BIT_FIELDS_LTOH` or `_BIT_FIELDS_HTOL`.
