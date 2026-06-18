# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/ddifm_impl.h

This is the private implementation header for DDI fault management. It includes DDI types and error queue support.

It defines internal FMA kstats, maximum ereport class size, stack depth, and symbol size. `i_ddi_errhdl` stores an error-handler callback and implementation argument. Fault-management resource cache structures track active access or DMA handles and bus-specific state.

`i_ddi_fmhdl` is the per-devinfo fault-management handle. It stores lock and owner, DMA/access caches, owning dip, kstat pointer, capability level, kstats, error queue, optional FMRI nvlist, interrupt block cookie, registered child targets, and bus-specific FM state.

PCI error table entries are represented by `pci_fm_err_t`, and `pci_err_tbl[]` is declared. Kernel-private declarations include global initialization, driver defect ereport posting, handler enter/exit/ownership checks, access/DMA error set and comparison-function getters, busop access enter/exit, busop FM init/fini, and FMA cache create/destroy.

Research notes:
- This header backs `ddifm.h` and is not driver-facing.
- `i_ddi_fmhdl` is referenced from `struct dev_info` in `ddi_impldefs.h`.
- Cache and handler ownership tracking are central to avoiding recursive or misattributed FMA handling.
