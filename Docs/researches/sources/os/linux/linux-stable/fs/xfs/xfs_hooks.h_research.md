# File Research: sources/os/linux/linux-stable/fs/xfs/xfs_hooks.h

## Purpose

Declares the optional live-hook abstraction for XFS and compiles it away when `CONFIG_XFS_LIVE_HOOKS` is disabled.

## Main Types and Macros

When live hooks are enabled:

- `struct xfs_hooks`
  - Wraps a `blocking_notifier_head`.
- `struct xfs_hook`
  - Embeds `struct notifier_block` as the first field.
- `xfs_hook_fn_t`
  - Typed hook callback adapter.
- `DEFINE_STATIC_XFS_HOOK_SWITCH`
- `xfs_hooks_switch_on`
- `xfs_hooks_switch_off`
- `xfs_hooks_switched_on`

When disabled:

- `struct xfs_hooks` is empty.
- Hook switches become no-ops.
- `xfs_hooks_call` returns `NOTIFY_DONE`.

## Main API

- `xfs_hooks_init`
- `xfs_hooks_add`
- `xfs_hooks_del`
- `xfs_hooks_call`
- `xfs_hook_setup`

## Important Invariants

- Static-branch enable/disable can take CPU hotplug locks, so callers must not hold locks that memory reclaim or writeback might also need while changing hook switch state.
- `xfs_hook_setup` sets callback and zero priority; users needing priority ordering must adjust the notifier field explicitly.

## Research Notes

This header is an optional instrumentation/control-plane API. Its design keeps hook call sites cheap in normal kernels and gives live features a common notifier-chain substrate.
