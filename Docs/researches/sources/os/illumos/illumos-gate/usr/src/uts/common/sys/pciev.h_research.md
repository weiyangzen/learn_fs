# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/pciev.h

## Purpose
Defines PCIe fabric error-event payload and I/O virtualization/domain bookkeeping structures used to track FMA-capable, non-FMA, and root-domain ownership across PCIe devices and bridges.

## Main Interfaces
- `pcie_eh_data_t`: packed error-handling data snapshot containing PCI status, PCI bridge status, PCI-X status/bridge/ECC data, PCIe device/AER/secondary/root-port status, and AER source IDs.
- Domain list structures:
  - `pcie_domains_t`
  - `pcie_req_id_list_t`
  - `pcie_child_domains_t`
- `pcie_domain_t`: per-device domain accounting; leaves cache one domain ID, bridges cache lists of child domain IDs and child BDFs.
- Domain lifecycle/list functions:
  - `pcie_domain_list_add()`
  - `pcie_domain_list_remove()`
  - `pcie_save_domain_id()`
  - `pcie_init_dom()`
  - `pcie_fini_dom()`
- Domain classification macros:
  - `PCIE_ASSIGNED_TO_FMA_DOM()`
  - `PCIE_ASSIGNED_TO_NFMA_DOM()`
  - `PCIE_ASSIGNED_TO_ROOT_DOM()`
  - `PCIE_BDG_HAS_CHILDREN_FMA_DOM()`
  - `PCIE_BDG_HAS_CHILDREN_NFMA_DOM()`
  - `PCIE_BDG_HAS_CHILDREN_ROOT_DOM()`
  - `PCIE_IS_ASSIGNED()`
  - `PCIE_BDG_IS_UNASSIGNED()`
  - `PCIE_IN_DOMAIN()`
- Leaf domain ID macros:
  - `PCIE_DOMAIN_ID_GET()`
  - `PCIE_DOMAIN_ID_SET()`
  - `PCIE_DOMAIN_ID_INCR_REF_COUNT()`
  - `PCIE_DOMAIN_ID_DECR_REF_COUNT()`
- Bridge list macros:
  - `PCIE_DOMAIN_LIST_GET()`
  - `PCIE_DOMAIN_LIST_ADD()`
  - `PCIE_DOMAIN_LIST_REMOVE()`
  - `PCIE_BDF_LIST_GET()`
  - `PCIE_BDF_LIST_ADD()`
  - `PCIE_BDF_LIST_REMOVE()`

## Dependencies And Relationships
Relies on `pcie_req_id_t`, `pcie_bus_t`, and classification helpers supplied by PCIe implementation headers. It is included by `pcie_impl.h` and used by fabric error handling and I/O virtualization domain routing.

## Research Notes
The file explicitly notes that domain-list access is currently lockless and may need revisiting with hotplug. Bridge domain state summarizes leaf children, while leaf devices store only their own assigned domain ID.
