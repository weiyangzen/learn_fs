# sources/test-tools/strace/bundled/linux/include/uapi/linux/pkt_sched.h

## Purpose

Defines the userspace ABI for Linux traffic-control queue disciplines and scheduler-specific netlink attributes. strace relies on these constants and structs to decode `RTM_NEWQDISC`, `RTM_NEWTCLASS`, `RTM_NEWTFILTER`, qdisc option blobs, and nested `TCA_*` attributes.

## Important APIs, Types, and Dependencies

The header depends on `linux/const.h` and `linux/types.h`. It exports generic priority constants, `struct tc_stats`, `struct tc_estimator`, traffic-control handle macros (`TC_H_MAJ`, `TC_H_MIN`, `TC_H_MAKE`, `TC_H_ROOT`, `TC_H_INGRESS`), link-layer/rate/size specs, and a long catalog of qdisc option structs and attribute enums. Covered qdiscs include FIFO, SKBPRIO, PRIO, MULTIQ, PLUG, TBF, SFQ, RED/GRED/CHOKE, HTB, HFSC, NETEM, DRR, MQPRIO, SFB, QFQ, CODEL, FQ_CODEL, FQ, HHF, PIE, FQ_PIE, CBS, ETF, CAKE, TAPRIO, ETS, and DUALPI2. Each family has one or more `struct tc_*_qopt`/`xstats` definitions plus `TCA_*_MAX` enum bounds.

## Control Flow, State, and Integration

The header is not executable; the operational flow is netlink message construction where `tcmsg` from rtnetlink carries a qdisc/class target and this header describes family-specific attribute payloads. Persistent state is kernel qdisc configuration and counters attached to network devices, classes, and offload-capable hardware.

## Risks and Test Signals

Risks are nested-attribute misdecoding, endian/width mistakes in rate and time fields, qdisc-specific structs changing while older tools still see raw blobs, and interpreting handle major/minor fields as stable semantic ids. Test signals include strace or netlink tests for each `TCA_*_MAX` family, handle macro display, `tc_stats` formatting, TAPRIO schedule entries, CAKE tin statistics, and unknown qdisc attributes preserved as raw netlink data.
