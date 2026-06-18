# File Research: sources/os/bsd/dragonflybsd/sys/sys/kbio.h

Defines keyboard ioctl ABI, keyboard modes, LED/lock state constants, keyboard metadata, repeat settings, keymap structures, accent/dead-key maps, function-key tables, and key return flags. It exposes user/kernel shared structures such as `keyboard_info_t`, `keyboard_repeat_t`, `keymap_t`, `accentmap_t`, `keyarg_t`, and `fkeyarg_t`.

Kernel-only compatibility structures support old keymaps. No direct VFS role, but it is a stable ioctl-facing system interface.
