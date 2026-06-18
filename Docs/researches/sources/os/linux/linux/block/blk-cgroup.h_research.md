# File Research: sources/os/linux/linux/block/blk-cgroup.h

## Scope

This private header defines block-cgroup core structures, policy interfaces, blkg lookup/reference helpers, configuration context declarations, delay helpers, and no-op stubs for builds without `CONFIG_BLK_CGROUP`.

## Major Types

- `struct blkcg_gq` represents one block-cgroup/request-queue association.
- `struct blkcg` embeds the cgroup css and owns blkg lookup structures, policy cpd pointers, stat llist heads, optional FC app id, and writeback list.
- `struct blkg_policy_data` is per blkg per policy.
- `struct blkcg_policy_data` is per blkcg per policy.
- `struct blkcg_policy` is the policy registration record with cftypes and cpd/pd alloc/init/online/offline/free/stat callbacks.
- `struct blkg_conf_ctx` carries parsed per-device config state.

## Core Helpers

- `css_to_blkcg()` converts css to blkcg.
- `blkg_lookup()` resolves a blkcg/queue pair using root fast path, `blkg_hint`, then radix tree.
- `blkg_to_pd()`, `blkcg_to_cpd()`, `pd_to_blkg()`, `cpd_to_blkcg()` convert policy data references.
- `blkg_get()`, `blkg_tryget()`, `blkg_put()` wrap the blkg percpu ref.
- `blkg_for_each_descendant_pre/post` macros traverse online descendant blkgs under cgroup traversal.
- Delay helpers:
  - `blkcg_use_delay()`, `blkcg_unuse_delay()`.
  - `blkcg_set_delay()`, `blkcg_clear_delay()`.
- Merge helper:
  - `blk_cgroup_mergeable()` requires matching blkg and matching root-issue classification.
- `bio_issue_as_root_blkg()` classifies metadata and swap I/O as root-issued for priority inversion avoidance.

## Dependencies

- Public block-cgroup and cgroup headers, blk-mq, llist, and internal `blk.h`.
- Request operation helpers and queue policy bitsets.

## Risks and Invariants

- `blkg_lookup()` must be called under RCU or with queue lock conditions satisfying `rcu_dereference_check()`.
- `blkg_get()` assumes the caller already holds a valid reference; RCU lookups should use `blkg_tryget()`.
- `blkcg_set_delay()` uses negative `use_delay` as a mutually exclusive mode and must not be mixed with increment/decrement delay users.
- The disabled-configuration stubs preserve buildability but remove all cgroup behavior and make merges unconditionally cgroup-compatible.
