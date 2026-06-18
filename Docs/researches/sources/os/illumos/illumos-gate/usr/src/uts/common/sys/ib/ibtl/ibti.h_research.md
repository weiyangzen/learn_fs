# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/ib/ibtl/ibti.h

## Purpose

`ibti.h` is the main public InfiniBand Transport Interface header for IBTF clients. It includes `ibti_common.h` and adds client-facing RC and UD channel allocation, query, modify, destination, and helper APIs.

## Main Types

`ibt_chan_alloc_flags_t` describes channel allocation options such as clone, user mapping, deferred allocation, SRQ, RSS, and Fibre Channel variants. `ibt_rc_chan_alloc_args_t`, `ibt_rc_chan_query_attr_t`, and `ibt_rc_chan_modify_attr_t` model RC channel creation, runtime state, path/RDMA parameters, and modifiable attributes. `ibt_ud_chan_alloc_args_t`, `ibt_ud_chan_query_attr_t`, and `ibt_ud_chan_modify_attr_t` do the same for UD channels, including Q_Key, P_Key index, RSS, SRQ, and FC attributes. `ibt_ud_dest_query_attr_t` captures resolved UD destination state.

## Functions

The prototypes cover RC/UD channel allocation, range allocation for consecutive UD QPNs, flush/free, query/modify, UD recovery from SQ error, UD destination allocation/modification/reply/SIDR request/free/query, privileged destination checks, Q_Key updates, channel private data, and channel-to-HCA GUID lookup.

## Research Notes

This is the high-level channel API most kernel consumers would use rather than explicit QP verbs. It hides much of the CI/HCA detail while still exposing RDMA-critical sizing, queue state, path, retry, SRQ, RSS, and Q_Key behavior.
