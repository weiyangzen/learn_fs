# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/ib/adapters/hermon/hermon_fm.h

## Purpose
Defines Hermon fault-management support: FMA structures, ereport classifications, device-error message strings, PIO retry/checking macros, test hooks, and FMA-related prototypes.

## Main Interfaces
- `struct i_hca_fm`: shared HCA FM state with refcount, lock, access-handle list, and cache.
- `struct i_hca_acc_handle`: wraps `ddi_acc_handle_t` with a linked-list node, lock, and active PIO thread count.
- `struct i_hca_fm_test`: optional `FMA_TEST` injection metadata.
- Type aliases:
  - `hermon_hca_fm_t`
  - `hermon_acc_handle_t`
  - `hermon_test_t`
- `HERMON_FMANOTE()` emits driver warning messages for likely hardware errors.
- Error strings cover CQE syndromes, EQE errors, HCR failures, firmware version, PCI ID, maintenance mode, and bad NVMEM.
- State flags distinguish PIO, DMA, ereport, callback, attach, and runtime FMA support.
- `hermon_pio_init()`, `hermon_pio_start()`, `hermon_pio_end()` wrap PIO operations with transient/persistent retry logic.

## Dependencies And Relationships
Includes Solaris FMA headers. Used by register mapping, PCI config access, command retry decisions, interrupt error polling, and attach/runtime hardware health paths.

## Research Notes
The PIO macros deliberately expand to a retrying `do { ... } while` pattern and require caller-supplied labels/status variables. This makes call-site control flow part of the interface contract.
