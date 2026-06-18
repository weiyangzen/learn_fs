# sources/test-tools/syzkaller/pkg/report/testdata/linux/report/430

Purpose: Linux reporter parse fixture for syzkaller. It expects `INFO: task hung in i2c_transfer`, alternate `hang in i2c_transfer`, type `HANG`, corrupted `N`, panicked `N`. The log contains many blocked syz-executor tasks in I2C read/ioctl paths.

Important APIs, types, and functions: this tests hung-task parsing and frame selection in I2C. Key frames include `i2c_transfer`, `i2c_transfer_buffer_flags`, `i2cdev_read`, `aspeed_i2c_master_xfer`, `i2c_smbus_xfer`, `i2cdev_ioctl_smbus`, and syscall read/ioctl frames.

Control flow: 268 log lines are parsed. The first blocked task stack selects `i2c_transfer`; subsequent blocked stacks are related noise and must not change the title.

State and persistence behavior: fixture headers persist expected title/type. Parser runtime state includes first-crash boundary and hang frame selection.

Dependencies, integration points, risks, and test signals: this protects hang grouping for I2C adapter lock/wait issues. Risks include choosing later SMBus ioctl stacks or generic rt-mutex helpers. Passing tests require HANG type, exact title/alternate, no panic, and no corruption.
