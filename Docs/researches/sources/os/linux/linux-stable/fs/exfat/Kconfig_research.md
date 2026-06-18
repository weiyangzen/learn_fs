# File Research: sources/os/linux/linux-stable/fs/exfat/Kconfig

This Kconfig file declares the Linux exFAT filesystem configuration options.

Key elements:
- `EXFAT_FS` is a tristate option named “exFAT filesystem support”.
- It selects `BUFFER_HEAD`, `NLS`, and `LEGACY_DIRECT_IO`, matching the implementation’s use of buffer-head based metadata I/O, charset conversion, and legacy direct I/O hooks.
- Help text states the module name is `exfat` and positions the filesystem for SD cards and USB storage.
- `EXFAT_DEFAULT_IOCHARSET` is a string option defaulting to `utf8`, dependent on `EXFAT_FS`.

Important behavior:
- The default charset setting controls the default user-visible filename conversion path between mount/user encoding and exFAT’s UTF-16 on-disk names.
- Runtime mount option `iocharset` can override this default.

Dependencies:
- Directly paired with `fs/exfat/Makefile`, which builds `exfat.o` only when `CONFIG_EXFAT_FS` is enabled.
