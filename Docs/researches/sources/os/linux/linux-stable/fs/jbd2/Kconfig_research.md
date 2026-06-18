# File Research: sources/os/linux/linux-stable/fs/jbd2/Kconfig

Defines JBD2 journaling configuration.

Options:
- `JBD2`: tristate generic journaling layer, selects `CRC32`, used by ext4 and OCFS2 and buildable as module `jbd2` unless required built-in by users.
- `JBD2_DEBUG`: optional runtime debugging support controlled via `/sys/module/jbd2/parameters/jbd2_debug` levels 0-5.

The help text positions JBD2 as a generic journal for block devices with 32-bit and 64-bit block number support.
