# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/ib/ibtl/ibvti.h

## Purpose

`ibvti.h` defines private verbs-level transport interface extensions. It exposes explicit QP and AH operations while mapping them onto the channel-oriented IBTI model.

## Main Content

The header provides compatibility aliases for CM reasons, SIDR status, open-channel flags, open arguments, CM event fields, request EEC fields, and address-vector fields. It defines `ibt_qp_hdl_t` as `ibt_channel_hdl_t`, making QPs usable in selected channel APIs.

## Functions

The verbs-style functions cover AH allocation/free/query/modify, QP allocation including special QPs, QP flush/initialize/free/query/modify, QP private data access, QP-to-HCA GUID lookup, UD QP recovery, SIDR destination QPN lookup through `ibt_ud_get_dqpn()`, module-specific failure creation, and OFUV CM request/proceed helper hooks.

## Research Notes

This file exists for lower-level or compatibility consumers that need QP/AH verbs terminology instead of the normal IBTI channel API. It is private, but it reveals how illumos preserves verbs-like behavior while the public interface prefers channels and UD destination handles.
