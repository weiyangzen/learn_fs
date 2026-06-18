# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/os/dacf_clnt.c

## Purpose

`dacf_clnt.c` implements the kernel-side clients of DACF. It connects device-minor creation and devinfo attach/detach lifecycle events to the core rule engine in `dacf.c`.

It also defines the synthetic `__kernel` DACF module descriptor `kmod_dacfsw`, which is mostly empty outside DEBUG builds.

## Minor Creation Matching

`dacfc_match_create_minor()` is called during minor-node creation. It checks whether a newly created minor node matches any DACF rule and, if so, creates deferred reservations on the devinfo node.

The function filters early:

- Clone devices are ignored unless they are network minor nodes.
- Minor nodes created outside attach are ignored because current DACF hooks only cover post-attach and pre-detach processing.

It builds match keys:

- Full device path from `ddi_pathname()`.
- `driver:minor` name when a minor name exists.
- Minor node type.

Rule matching is performed from most specific to least specific:

1. `device-path`
2. `driver-minorname`
3. `minor-nodetype`

It repeats that ordering separately for `post-attach` and `pre-detach`. Matches allocate `dacf_rsrvlist_t` entries and link them into `DEVI(dip)->devi_dacf_tasks`.

## Recursion Avoidance

Before matching, `dacfc_match_create_minor()` checks `DEVI_IS_INVOKING_DACF(dip)` under `devi_lock`. If a DACF operation is currently being invoked for the same devinfo node, matching is aborted with a warning. This prevents a configuration operation from recursively creating a minor node and deadlocking on the same devinfo task machinery.

## Post-Attach Handling

`dacfc_postattach()` invokes all post-attach reservations for the devinfo node with `dacf_process_rsrvs(..., DACF_PROC_INVOKE)`. It then scans the reservation list for failed post-attach operations.

A failure sets `DACF_FAILURE`; optional debug logging reports the affected device path. The function does not release reservations after invocation, leaving them available for later cleanup or pre-detach flow.

## Pre-Detach Handling

`dacfc_predetach()` invokes all pre-detach reservations and checks whether any failed. If a pre-detach operation fails, it makes one attempt to re-run post-attach operations through `dacfc_postattach()` to restore a sane configuration state.

Debug logging can report both the failed unconfiguration and whether re-autoconfiguration succeeded.

## Kernel DACF Module

The file defines `kmod_dacfsw`, registered by `dacf_init()` as the special `__kernel` DACF module. In DEBUG builds it exposes a test post-attach operation under the `kmod_test` opset. In non-DEBUG builds the kernel module has no opsets but is still registered so kernel-supplied DACF operations can exist without loadable modules.

## Dependencies

`dacf_clnt.c` depends on the core DACF APIs:

- `dacf_match`
- `dacf_rsrv_make`
- `dacf_process_rsrvs`
- `dacf_get_arg`

It also uses DDI/devinfo internals, minor data, driver names, device paths, and DACF debug flags.

## Research Notes

This file is the bridge between rule matching and actual device lifecycle events. The key semantic detail is reservation: matching occurs during minor creation, but operation invocation happens later at attach/detach boundaries. The highest-risk areas are the recursion guard, exact match priority, clone-device filtering, and recovery behavior when pre-detach fails.
