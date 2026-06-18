# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/ib/ibtl/ibtl_status.h

## Purpose

`ibtl_status.h` defines global IBTL return codes and work-completion status values.

## Status Families

`ibt_status_t` starts with generic return codes such as success, failure, unsupported, invalid parameter, insufficient resources, CM failure, missing HCA/path/service/MCG/node records, IP-to-GID failures, and no-such-object. It then groups errors by resource/HCA, HCA attributes, UD destinations, channels, completion queues, reserved opaque ranges, memory operations, multicast, P_Key lookup, protection domains, SRQs, and FMR pools.

Opaque status slots are deliberately reused by `ibci.h` and `ibtl_ci_types.h` for legacy or CI-specific meanings such as RDD/EEC and raw datagram errors.

## Completion Status

`ibt_wc_status_t` is a compact `uint8_t`. The file defines success plus local length/protection/channel errors, flushed WRs, memory-management/bind errors, and reliable transport errors such as bad response, local access, remote invalid request/access/op errors, transport timeout, and RNR NAK timeout.

## Research Notes

This is the canonical status vocabulary for IBTF callers and HCA drivers. The numeric grouping is useful when tracing failures across layers: immediate API failures use `ibt_status_t`, while completed work requests report `ibt_wc_status_t`.
