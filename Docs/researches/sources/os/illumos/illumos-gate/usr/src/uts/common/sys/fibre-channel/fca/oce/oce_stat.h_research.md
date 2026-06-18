# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/fibre-channel/fca/oce/oce_stat.h

This header defines the OCE driver's kstat-facing statistics structure and stat lifecycle functions.

Key contents:
- `struct oce_stat`, a collection of `kstat_named_t` counters for:
  - RX/TX bytes and frames;
  - RX/TX errors and drops;
  - unicast/multicast/broadcast frame counts;
  - CRC, alignment, range, frame-too-long, address-match, checksum, FIFO, and control/pause frame counters;
  - hardware drop reasons such as no packet buffers, missing descriptors, too many fragments, invalid ring, MTU drops, runt/short/header/tcp-length drops, and no-fragment drops.
- `oce_stat_init()` and `oce_stat_fini()` prototypes.

Dependencies:
- Includes `oce_hw_eth.h` and `oce_impl.h`.
- Uses `kstat_named_t` through `oce_impl.h`.

Research notes:
- The fields correspond closely to `mbx_get_nic_stats` and nested RX/TX stats in `oce_hw_eth.h`.
- This is the public driver-observability surface for OCE hardware counters inside illumos kstats.
