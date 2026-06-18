# File Research: sources/os/linux/linux/fs/xfs/xfs_hooks.h

Declares optional XFS live hook infrastructure and compiles it away when `CONFIG_XFS_LIVE_HOOKS` is disabled.

Key elements:
- With live hooks enabled, `struct xfs_hooks` wraps a `blocking_notifier_head`, and `struct xfs_hook` embeds a leading `notifier_block`.
- Defines static branch helper macros for hook-switch declaration, on/off, and checked-on tests.
- Declares hook chain initialization, registration, unregistration, call, and `xfs_hook_setup`.
- With live hooks disabled, provides empty structs/no-op macros and makes calls return `NOTIFY_DONE`.

Dependencies:
- Uses Linux blocking notifier chains and static keys/jump labels.
- Callers must handle static-branch patching constraints noted in the header comments.

Research notes:
- The header warns that static branch updates take the CPU hotplug lock, so callers must avoid holding locks that memory reclaim/writeback might need while switching hooks on or off.
