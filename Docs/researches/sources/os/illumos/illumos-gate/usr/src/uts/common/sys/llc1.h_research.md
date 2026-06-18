# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/llc1.h

## Role

Internal LLC Class 1 STREAMS mux header compatible with SunConnect LLC2/DLPI expectations.

## Structure

Defines LLC statistics and stat indexes, multicast table entries, per-lower-MAC state (`llc_mac_info_t`), per-stream state (`llc1_t`), per-device state (`llc1dev_t`), link/stream/debug flags, module watermarks, LLC/SNAP address and header structures, protocol constants, special LLC ioctls, and a local `qelem` queue structure.

## Dependencies And Consumers

The header assumes surrounding kernel networking/STREAMS types such as `queue_t`, `mblk_t`, `kmutex_t`, `krwlock_t`, `kstat_t`, and `ETHERADDRL` are available from including implementation files.

## Important Details

The structures embed STREAMS queues and mblk pointers directly, so they are driver-private implementation state rather than stable user ABI. The ioctl values (`L_GETPPA`, `L_SETPPA`, `L_GETSTATS`, `L_ZEROSTATS`) are retained for LLC2 conformance behavior.

## Research Notes

Read completely: 278 lines, 8102 bytes.
