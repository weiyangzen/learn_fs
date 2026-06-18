# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/log.h

## Role

Kernel log device/STREAMS internal header for `/dev/conslog` and `/dev/log` clone handling.

## Structure

Defines minor numbers, clone index range, module ID, packet sizes, queue watermarks, dump-message magic, recent/free cache sizes, `log_t`, `log_filter_t`, per-zone clone array `log_zone_t`, and dump-message header `log_dump_t`. Kernel builds declare global queues, filters, and log management functions.

## Dependencies And Consumers

Includes `sys/types.h`, `sys/strlog.h`, and `sys/stream.h`. Consumers are kernel log driver and console/log message paths.

## Important Details

`log_t` is zone-aware via `zoneid_t`, and `log_zone_t` tracks active clone types. `log_dump_t` stores checksums for queued unsent messages and is tied to `dump_messages()` layout.

## Research Notes

Read completely: 123 lines, 3932 bytes.
