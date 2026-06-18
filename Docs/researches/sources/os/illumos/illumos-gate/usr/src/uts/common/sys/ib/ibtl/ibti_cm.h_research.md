# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/ib/ibtl/ibti_cm.h

## Purpose

`ibti_cm.h` defines the IBTI Communication Manager event, status, private-data, reject, redirect, and callback contract. It is the public shape of RC connection establishment/teardown and UD SIDR service resolution.

## Main Content

The header defines CM private-data limits for REQ, REP, RTU, MRA, DREQ, DREP, LAP, APR, REJ, SIDR request/reply, and RDMA IP CM private headers. `ibt_cm_reason_t` enumerates standard reject/failure reasons and illumos-specific values such as duplicate requests, aborts, CI failures, invalid passive QP state, and RDMA IP CM rejection.

`ibt_cm_status_t` models client handler decisions: accept, reject, redirect, no channel/resource, default, or defer. SIDR and alternate-path status enums capture UD service resolution and LAP/APR outcomes.

## Event Structures

The header defines redirect data, REP/MRA/LAP/APR/failure event payloads, REQ event payloads, RDMA IP reject information, additional reject unions, connection-closed reason codes, and the top-level `ibt_cm_event_t`. It also defines return structures for accepting, rejecting, redirecting, and proceeding after deferred CM handling.

For UD/SIDR, `ibt_cm_ud_event_t` carries SIDR request/reply events and `ibt_cm_ud_return_args_t` carries service response or redirect data.

## Callbacks

`ibt_cm_handler_t` is the RC CM event callback type. `ibt_cm_ud_handler_t` is the UD CM/SIDR callback type. The comments emphasize that blocking work in CM callbacks can stall CM threads, and that deferred events must later be completed with the proceed APIs declared in `ibti_common.h`.

## Research Notes

This file is the semantic contract for connection lifecycle, private negotiation data, redirect handling, and failure reporting. RDMA storage consumers that use RC or RDMA IP CM rely on these structures to safely establish channels and interpret rejection or teardown.
