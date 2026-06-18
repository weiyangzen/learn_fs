# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/aggr_lacp.h

## Purpose

`aggr_lacp.h` defines kernel-private IEEE 802.3ad LACP protocol state, timers, packet formats, and statistics for link aggregation.

## State Machines

The header defines receive, periodic, mux, and churn state enums plus string-list macros for diagnostics. Timer constants include fast/slow periodic times, short/long timeout times, churn detection time, and aggregate wait time.

`Agg_t` stores per-aggregation actor/partner system information, keys, transmit/receive enable flags, collector delay, periodic timer mode, last-change time, and readiness. `aggr_lacp_port_t` stores actor and partner port identifiers, state bytes, per-port state machine variables, timers, timer-thread state, mutex/CV, and last event time.

## Packet Formats

`lacp_t` describes an LACPDU with actor, partner, collector, terminator, and reserved fields. `marker_pdu_t` describes marker protocol frames. `lag_id_t` represents the 802.3ad LAG identifier.

## Research Notes

This file is protocol-structure oriented. Correctness depends on byte/bit layout matching 802.3ad and timer-thread handling matching the aggregation driver’s port lifecycle.
