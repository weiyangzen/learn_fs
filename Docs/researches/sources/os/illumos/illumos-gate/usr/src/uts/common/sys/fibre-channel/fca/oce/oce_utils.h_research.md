# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/fibre-channel/fca/oce/oce_utils.h

This header defines OCE utility macros, logging controls, endian/dword swapping, address helpers, simple list structures, list APIs, atomic reservation, and RSS hash-key generation.

Key contents:
- Logging module masks for config, TX, RX, and ISR.
- Default and maximum log-setting masks.
- `oce_log()` macro, routing messages through `cmn_err()` based on per-device module mask and severity.
- Delay macros `OCE_USDELAY` and `OCE_MSDELAY`.
- Utility macros for log2, address low/high extraction, 64-bit address construction, pointer casts, 4K page offset, and page-count calculation.
- Debug-only `OCE_DUMP()` word dump macro.
- `OCE_DW_SWAP()` and endian-selective `DW_SWAP()` for big-endian conversion of dword buffers.
- Intrusive doubly linked list node `OCE_LIST_NODE_T` and locked list header `OCE_LIST_T`.
- List API prototypes and convenience macros for create/destroy/insert/remove/empty/size/link-init.
- `oce_atomic_reserve()` prototype.
- `oce_gen_hkey()` prototype for generating an RSS hash key.

Dependencies:
- Includes `sys/types.h` and `sys/list.h`.
- Uses `kmutex_t`, `cmn_err`, `CE_*`, `drv_usecwait`, `highbit`, `howmany`, `BMASK_32`, and byteorder macros via including context.

Research notes:
- The list type is driver-local rather than illumos `list_t`; it carries its own mutex and item count.
- The logging macro depends on `OCE_MOD_NAME` and `struct oce_dev` fields from `oce_version.h`/`oce_impl.h`, so include order matters.
- `OCE_DW_SWAP()` is used for firmware/hardware command buffers on big-endian platforms.
