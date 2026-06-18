# File Research: sources/os/bsd/freebsd-src/sys/sys/tiio.h

## Scope

This header defines user-visible ioctl data structures and request codes for Alteon/Tigon network adapter diagnostics, statistics, parameters, tracing, and firmware/register/memory access.

## APIs And Constants

- Defines `struct ti_stats`, a fixed-layout Tigon statistics block with MAC counters, MIB-II/RFC-derived interface counters, 64-bit high-capacity counters, host command counters, NIC events, ring manipulation counters, interrupt/coalescing counters, DMA attention counters, resource exhaustion counters, MAC RX/TX attention counters, collision histogram, profile slots, and padding to a 1024-byte block.
- Defines interface admin/oper status constants such as `IF_ADMIN_STATUS_UP`, `IF_OPER_STATUS_DOWN`, and related status values.
- Defines `struct tg_reg` for adapter register access and `struct tg_mem` for adapter memory access.
- Defines `ti_param_mask` flags for statistic tick, RX/TX coalescing ticks, RX/TX coalescing buffer descriptors, TX buffer ratio, and all supported parameters.
- Defines `struct ti_params` containing tunable coalescing/statistics parameters plus a mask of active fields.
- Defines `ti_trace_type` bit flags for trace categories and trace levels.
- Defines `struct ti_trace_buf` for trace buffer exchange.
- Defines FreeBSD driver ioctls `TIIOCGETSTATS`, `TIIOCGETPARAMS`, `TIIOCSETPARAMS`, `TIIOCSETTRACE`, and `TIIOCGETTRACE`.
- Defines Alteon-compatible ioctls `ALT_ATTACH`, `ALT_READ_TG_MEM`, `ALT_WRITE_TG_MEM`, `ALT_READ_TG_REG`, and `ALT_WRITE_TG_REG`.

## Control Flow And Integration

- Driver ioctl handlers use these structures to copy statistics, apply selected tunables, enable trace categories, return trace buffers, and perform diagnostic register/memory operations.
- The statistics structure embeds firmware/hardware-visible counters and marks most fields `volatile`, reflecting that values may be updated by device/firmware paths.
- `param_mask` lets userland set only selected tuning fields rather than replacing the whole parameter set.
- Alteon ioctl values preserve compatibility with vendor tooling while avoiding vendor ioctl numbers 1 through 6.

## Dependencies

- Includes `<sys/ioccom.h>` for `_IO`, `_IOR`, `_IOW`, and `_IOWR`.
- Uses kernel/public integer types, `caddr_t`, `u_long`, and ioctl encoding conventions.
- Tied to the Tigon/Alteon network driver implementation and its firmware statistics layout.

## Risks And Invariants

- `struct ti_stats` layout is externally visible and firmware-derived; field order, sizes, and total padded size must remain stable for ioctl consumers.
- Register and memory access ioctls are powerful diagnostics and must be permission-checked by driver code.
- Trace buffer pointers are user addresses and require careful copyin/copyout handling.
- `volatile` does not provide synchronization by itself; the driver must still snapshot or serialize where consistency matters.
