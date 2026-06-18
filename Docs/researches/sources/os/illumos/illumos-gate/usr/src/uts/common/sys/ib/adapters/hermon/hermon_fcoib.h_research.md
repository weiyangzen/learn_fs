# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/ib/adapters/hermon/hermon_fcoib.h

## Purpose
Defines Fibre Channel over InfiniBand support state and helper prototypes for FEXCH/RFCI QP and MPT/MTT resource management.

## Main Interfaces
- `hermon_fcoib_qp_t`: FCoIB QP resource plus vmem arena pointer.
- `hermon_fcoib_t`: global FCoIB state including queried limits, lock, shared FEXCH MPT/MTT/QP resources, per-port enable flags, per-port counts, per-port vmem arenas, N_Port IDs, and base indexes for MPT, MTT, FEXCH QPs, and RFCI QPs.
- Prototypes cover source ID mapping, FEXCH base/offset validation, QP number and mkey translation, per-FEXCH MKEY init/fini, relative QPN lookup, and FCoIB init/fini.

## Dependencies And Relationships
Depends on `HERMON_MAX_PORTS`, resource handles, `ibt_fc_attr_t`, and PD handles from the wider driver. Ties into FCoIB command structures and QP/MR functions in `hermon_cmd.h`, `hermon_qp.h`, `hermon_mr.h`, and `hermon_hw.h`.

## Research Notes
This header is small but important for reserved-resource partitioning: FCoIB owns ranges of MPTs, MTTs, FEXCH QPs, and RFCI QPs per port.
