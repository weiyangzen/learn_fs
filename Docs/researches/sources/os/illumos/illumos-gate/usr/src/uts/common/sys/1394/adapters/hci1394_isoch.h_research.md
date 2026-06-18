# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/1394/adapters/hci1394_isoch.h

This private HAL header declares front-end isochronous support and the soft-state structures used by `hci1394` isochronous DMA.

Main types:
- `hci1394_isoch_handle_t`: opaque module handle.
- `hci1394_idma_desc_mem_t`: tracks allocated descriptor DMA memory, including multi-cookie DMA segments, used byte counts, and offsets.
- `hci1394_iso_ctxt_t`: one transmit or receive context, including context index/mode/flags, interrupt coordination primitives, speed/channel, register pointer, descriptor/xfer-control lists, IXL execution state, DMA recovery thresholds, default tag/sync/skip settings, and target stop callback.
- `hci1394_intr_thresh_t`: interrupt storm accounting for cycle lost/inconsistent events.
- `hci1394_isoch_t`: module-level state containing interrupt thresholds, transmit/receive context counts, context arrays of size `HCI1394_MAX_ISOCH_CONTEXTS`, and a context list mutex.

Key APIs:
- Module lifecycle/resume/error interrupt control: `hci1394_isoch_init`, `fini`, `resume`, `cycle_lost`, `cycle_inconsistent`, `error_ints_enable`.
- Context lookup/count helpers for receive and transmit.
- HAL entry points for local isoch DMA allocate/free/start/update/stop and `hci1394_do_stop`.

Concurrency notes:
- Per-context `intrprocmutex` protects `intr_flags`.
- Context list mutex protects context allocation/in-use state.
- Interrupt flags distinguish stopped, pending interrupt, in interrupt processing, in update, and in callback states.
