# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/pcie_impl.h

## Purpose
Defines private PCIe nexus and fabric implementation state: device/bus classification macros, config/capability access shortcuts, fault-management register snapshots, root fault/error-source data, fabric tuning state, per-bus private data, fault queues, scan/error status flags, and PCIe nexus/fabric/link/error-management prototypes.

## Main Interfaces
- Bus-private lookup and classification macros:
  - `PCIE_DIP2BUS()`
  - `PCIE_DIP2UPBUS()`
  - `PCIE_DIP2DOWNBUS()`
  - `PCIE_DIP2PFD()`
  - `PCIE_BUS2DIP()`
  - `PCIE_BUS2DOM()`
  - `PCIE_IS_PCIE()`
  - `PCIE_IS_PCIX()`
  - `PCIE_IS_PCI()`
  - `PCIE_HAS_AER()`
  - `PCIE_IS_ROOT()`
  - `PCIE_IS_RC()`
  - `PCIE_IS_RP()`
  - `PCIE_IS_SWU/SWD/SW()`
  - `PCIE_IS_BDG()`
  - `PCIE_IS_PCIE_BDG()`
- Config/cap access macros:
  - `PCIE_GET()`, `PCIE_PUT()`
  - `PCIE_CAP_GET()`, `PCIE_CAP_PUT()`
  - `PCIE_AER_GET()`, `PCIE_AER_PUT()`
  - `PCIX_CAP_GET()`, `PCIX_CAP_PUT()`
- Hotplug mode enum:
  - `pcie_hp_mode_t`
- Fault/error register snapshot structures:
  - `pf_pci_bdg_err_regs_t`
  - `pf_pci_err_regs_t`
  - `pf_pcix_ecc_regs_t`
  - `pf_pcix_err_regs_t`
  - `pf_pcix_bdg_err_regs_t`
  - `pf_pcie_adv_bdg_err_regs_t`
  - `pf_pcie_adv_rp_err_regs_t`
  - `pf_pcie_adv_err_regs_t`
  - `pf_pcie_rp_err_regs_t`
  - `pf_pcie_err_regs_t`
  - `pf_pcie_slot_regs_t`
- Root fault/source structures:
  - `pf_intr_type_t`
  - `pf_root_eh_src_t`
  - `pf_root_fault_t`
- Link and fabric enums:
  - `pcie_link_width_t`
  - `pcie_link_speed_t`
  - `pcie_link_flags_t`
  - `pcie_lbw_state_t`
  - `pcie_tag_t`
  - `pcie_fabric_flags_t`
- `pcie_fabric_data_t`: hierarchy-wide MPS/tag settings and fabric flags.
- `pcie_bus_t`: core per-node PCIe private state including DIPs, config handle, BDFs, capability offsets, bus ranges, assigned addresses, hotplug state, ARI, link state, link-bandwidth monitoring state, domain, and root-port fabric data.
- Fault queue/data structures:
  - `pf_affected_dev_t`
  - `pf_data_t`
  - `pf_impl_t`
- FM and scan flags:
  - `PF_FM_*`
  - `PF_ADDR_*`
  - `PF_SCAN_*`
  - `PF_ERR_*`
  - `PF_ERR_FATAL_FLAGS`
- Pseudo device types:
  - `PCIE_PCIECAP_DEV_TYPE_RC_PSEUDO`
  - `PCIE_PCIECAP_DEV_TYPE_PCI_PSEUDO`
- Nexus/fabric/link/error APIs:
  - `pcie_init()`, `pcie_uninit()`
  - `pcie_open()`, `pcie_close()`, `pcie_ioctl()`, `pcie_prop_op()`
  - `pcie_fabric_setup()`
  - `pcie_initchild()`, `pcie_uninitchild()`
  - `pcie_init_bus()`, `pcie_fini_bus()`
  - `pcie_fab_init_bus()`, `pcie_fab_fini_bus()`
  - `pcie_rc_init_bus()`, `pcie_rc_fini_bus()`
  - `pcie_enable_errors()`, `pcie_disable_errors()`, `pcie_enable_ce()`
  - `pcie_ari_*()`
  - `pf_*()` scan/handler helpers
  - `pciev_*()` error/domain helpers
  - `pcie_link_bw_*()`
  - `pcie_link_set_target()`
  - `pcie_link_retrain()`

## Dependencies And Relationships
Includes `pcie.h`, `pciev.h`, and taskq internals. This is used by `pciex`, root-complex, bridge, hotplug, and fabric error-management implementation code.

## Research Notes
`pcie_bus_t` is the central nexus-private record. The file distinguishes static device data, last fault data, hotplug state, ARI state, link-management state, bandwidth monitoring state, and fabric-wide tuning data.
