# File Research: sources/os/linux/linux/fs/jbd2/Kconfig

Defines JBD2 journaling configuration.

Options:
- `JBD2`: tristate generic journaling layer for block devices with 32-bit and 64-bit block numbers; selects `CRC32`; used by ext4 and OCFS2.
- `JBD2_DEBUG`: optional runtime debugging support, controlled through `/sys/module/jbd2/parameters/jbd2_debug` levels 0-5.

The config text notes module constraints when dependent filesystems are built in.
