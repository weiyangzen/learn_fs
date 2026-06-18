# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/fibre-channel/fca/emlxs/emlxs_os.h

## Purpose

Collects OS compatibility, feature-selection macros, Solaris/illumos kernel includes, weak symbol declarations, endian selection, utility macros, unsolicited buffer structures, error translation structures, and default driver patch masks for `emlxs`.

## Main Definitions

### Feature and Platform Gates

Defines driver feature macros:

- `DHCHAP_SUPPORT`
- `SATURN_MSI_SUPPORT`
- `MENLO_SUPPORT`
- `MBOX_EXT_SUPPORT`
- `DUMP_SUPPORT`
- `SAN_DIAG_SUPPORT`
- `FMA_SUPPORT`
- `NODE_THROTTLE_SUPPORT`

For `S11`, enables `MSI_SUPPORT`, `SFCT_SUPPORT`, `MODFW_SUPPORT`, and sets `EMLXS_MODREV` to the NPIV-capable revision. `SFCT_SUPPORT` enables `MODSYM_SUPPORT` and `FCIO_SUPPORT`.

Defines `S10S11` for Solaris 10/11 compatibility and fallback `EMLXS_MODREV`/`EMLXS_MODREVX` values.

### Includes and Compatibility Constants

Includes a large set of kernel, DDI, SCSI, FMA, and Fibre Channel headers. For non-S11 builds it defines PCI/PCIe capability constants that newer headers would otherwise provide.

Defines fallback constants for FC speeds, default SID/DID, relaxed DMA ordering, taskq flags, burst sizes, and boolean values.

### Utility Macros

- `PADDR_LO`, `PADDR_HI`, `PADDR` for 64-bit physical address splitting/combining.
- `BUSYWAIT_MS`, `BUSYWAIT_US`.
- `EMLXS_MPDATA_SYNC` wrapper around `ddi_dma_sync`.
- `PKT2PRIV` and `PRIV2PKT`.
- DMA direction/status constants.
- BAR/register index constants.
- `DEAD_PTR` width-sensitive poison value.

### Unsolicited Buffer Structures

`emlxs_ub_priv_t` tracks private state for an unsolicited buffer, including FC buffer pointer, port, BPL DMA state, IP buffer DMA cookies, FC-4 type, flags, timeout, command/token, pool pointer, and linkage.

`emlxs_unsol_buf_t` tracks an unsolicited-buffer pool: pool linkage, type, buffer size, counts, flags, free/reserved counts, token range, and `fc_unsol_buf_t` array.

### Error and Table Structures

- `emlxs_xlat_err_t`: maps internal `emlxs_status` to packet state/reason/explanation/action.
- `emlxs_table_t`: generic code-to-string table entry.

### Patch Masks

Defines `EMLXS_PATCH1` through `EMLXS_PATCH32`, then names default ULP and FCP underrun patches. `DEFAULT_PATCHES` includes auto-response/ULP workarounds and residual underrun fixes.

## Integration Notes

This is an umbrella compatibility header and is likely included very early by most driver files. It controls which other headers and APIs are visible.

## Risks and Gotchas

- Feature behavior is compile-time controlled; changing one macro can alter ABI-visible structures and enabled code paths.
- Weak symbol usage allows one binary to tolerate missing platform APIs, but call sites must check availability correctly.
- `EMLXS_MPDATA_SYNC` is a multi-statement macro without `do { } while (0)`, so use in conditional contexts needs care.
- The unsolicited-buffer structures combine kernel allocation, DMA handles, token accounting, timeout state, and pool linkage; synchronization is not defined here and must be enforced by users.
