# sources/user-network-fs/nfs-ganesha/src/include/log_common.h

## Purpose

`log_common.h` provides shared logging enums separated from the heavier logging API. It defines severity levels, component identifiers, and conditional logging match policy values used by log configuration, DBus, macros, and subsystem code.

## Important APIs, Types, and Functions

`log_levels_t` ranges from `NIV_NULL` through `NIV_FULL_DEBUG`, with `NB_LOG_LEVEL` as a bound. `log_components_t` enumerates all server components such as FSAL, NFS protocol, exports, file handles, dispatch, MDCACHE, duplicate requests, init, idmapper, NLM, TIRPC, callbacks, state, DBus, QoS, recovery, and RDMA. `cond_log_match_policies_t` defines any/all client/export matching.

## Control Flow

This header has no runtime code, but enum values drive array indexing in `component_log_level` and `LogComponents`, config parsing, and `isLevel` decisions in `log.h`.

## State and Persistence Behavior

No state is stored here. The enum ordering is persistent in the sense that logs, configs, DBus views, and arrays depend on stable component indexes.

## Dependencies and Integration Points

The file has no includes, making it safe for broad inclusion. It is consumed by logging facilities, config parsers, generated diagnostics, and subsystem code that declares its component.

## Risks and Test Signals

Adding or reordering components can break array initializers and external tooling that expects names/order. Tests should verify every enum has a matching `LogComponents` entry, config names map to the intended component, level strings round trip, and `COMPONENT_COUNT` bounds all arrays.
