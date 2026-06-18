# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/fibre-channel/fca/qlc/ql_isr.h

## Role

`ql_isr.h` declares interrupt-handling interfaces and interrupt tuning globals for the `qlc` Fibre Channel adapter driver.

## Major Definitions

The file defines `MAX_SPURIOUS_INTR` as `4` and declares two global counters/tuning values:
- `ql_spurious_cnt`
- `ql_max_intr_loop`

## Interfaces

The interrupt entry points are:
- `ql_isr`, the main ISR callback.
- `ql_isr_aif`, an alternate interrupt function handler.
- `ql_isr_default`, the default interrupt handler.
- `ql_disable_intr` and `ql_enable_intr` for adapter interrupt masking.

## Integration Notes

The declarations depend on illumos interrupt callback types (`uint_t`, `caddr_t`) and the driver state type `ql_adapter_state_t`. The header does not define interrupt status bits; those are supplied by hardware and mailbox/register headers.
