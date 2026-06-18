# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/aggr_impl.h

## Purpose

`aggr_impl.h` defines kernel-private data structures and functions for the link aggregation MAC driver.

## Main Structures

The file models pseudo receive and transmit groups/rings that present aggregated underlying NIC rings to MAC clients. `aggr_port_t` represents one member link with MAC client/handle state, link status, stats, LACP state, hardware group/ring references, promiscuous supplemental addresses, and TX ring mappings.

`aggr_grp_t` represents an aggregation group with link id, key, refs, port list, group MAC, flags, MAC registration, transmit port array and policy, stats, LACP aggregate state, checksum/LSO capabilities, queued LACP packet thread state, pseudo RX/TX groups, TX flow-control notification thread state, and port callback synchronization.

## Interfaces

The header declares initialization/finalization, ioctl init/fini, group create/delete/info/modify/port add/remove, port create/delete/start/stop/promisc/unicast/multicast/stat, receive/transmit callbacks, LACP mode and packet handling, VLAN/MAC classification helpers, and ring TX helpers.

## Research Notes

This header is concurrency-heavy. It uses atomic refcount macros, multiple mutex/CV domains, LACP deferred processing to avoid MAC perimeter deadlocks, and explicit group/port lock ordering.
