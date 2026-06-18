# File Research: sources/os/linux/linux-stable/fs/xfs/xfs_hooks.c

## Purpose

Implements a small wrapper around Linux blocking notifier chains for optional XFS live hooks.

## Main API

- `xfs_hooks_init`
  - Initializes a hook chain with `BLOCKING_INIT_NOTIFIER_HEAD`.
- `xfs_hooks_add`
  - Registers a hook notifier and asserts that the callback is present and that `struct xfs_hook` embeds `notifier_block` at offset zero.
- `xfs_hooks_del`
  - Unregisters a hook from a chain.
- `xfs_hooks_call`
  - Invokes the blocking notifier chain and returns the final notifier status.

## Important Invariants

- `struct xfs_hook` must remain layout-compatible with `struct notifier_block` at offset zero.
- Callers are responsible for static-key gating through the header macros so empty hook sites can be compiled or patched to near-zero overhead.

## Dependencies

Uses Linux blocking notifier APIs and XFS trace/mount/ag include context. The concrete hook points live elsewhere; this file only provides generic chain mechanics.

## Research Notes

This is deliberately minimal infrastructure. It does not define hook semantics, event payloads, or lifecycle beyond registration and call dispatch.
