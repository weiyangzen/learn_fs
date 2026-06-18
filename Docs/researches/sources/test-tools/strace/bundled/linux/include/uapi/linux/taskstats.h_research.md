# sources/test-tools/strace/bundled/linux/include/uapi/linux/taskstats.h

## Purpose

Defines the generic netlink task accounting ABI. strace uses it to decode taskstats messages reporting per-task exit, delay accounting, basic accounting, I/O accounting, context switches, executable identity, and delay extrema.

## Important APIs, Types, and Dependencies

The header depends on `linux/types.h` and `linux/time_types.h`. `TASKSTATS_VERSION` is 17 and `TS_COMM_LEN` is 32. `struct taskstats` is a versioned append-only ABI containing exit code, flags, nice, CPU/blkio/swapin/freepages/thrashing/compact/wpcopy/irq delay counts/totals/min/max/timestamps, runtime fields, command, scheduling, uid/gid/pid/ppid/tgid, start time, elapsed/user/system times, page faults, memory usage, high watermarks, I/O byte/syscall counters, scaled times, executable device/inode, and v17 max-delay timestamps. Command/type/attribute enums define generic netlink request and aggregation payloads. `TASKSTATS_GENL_NAME` and version identify the family.

## Control Flow, State, and Integration

Runtime flow is generic netlink registration, request by pid/tgid or CPU mask, and kernel event delivery when tasks exit. State is accumulated in task accounting and delay-accounting subsystems; some fields only update when accounting is enabled.

## Risks and Test Signals

Risks include struct version drift, alignment errors around 64-bit fields, interpreting delay totals without checking accounting availability, and 32-bit `ac_btime` overflow despite the v10 64-bit field. Test signals include netlink command/type decode, full `struct taskstats` formatting, v17 timestamp fields, and aggregation by PID/TGID.
