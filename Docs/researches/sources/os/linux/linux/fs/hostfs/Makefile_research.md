# File Research: sources/os/linux/linux/fs/hostfs/Makefile

Purpose: Builds UML hostfs objects and links the kernel-side filesystem with user-space syscall bridge objects.

Key content:
- Defines `hostfs-objs := hostfs_kern.o`.
- Adds `hostfs_user.o` and `hostfs_user_exp.o` to built-in hostfs support when `CONFIG_HOSTFS` is enabled.
- Adds `hostfs.o` under `obj-$(CONFIG_HOSTFS)`.
- Includes UML-specific `arch/um/scripts/Makefile.rules`.

Dependencies and integration:
- Hostfs is specific to User-Mode Linux and depends on UML build rules for user/kernel object handling.

Risk notes:
- Split object handling is unusual: kernel-facing code and exported user syscall bridge symbols are built together through UML-specific rules.
