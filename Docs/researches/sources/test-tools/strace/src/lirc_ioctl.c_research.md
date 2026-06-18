<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/lirc_ioctl.c -->
# sources/test-tools/strace/src/lirc_ioctl.c

Purpose: decodes Linux infrared remote control ioctl commands.
Important APIs/types/functions: `lirc_ioctl`, LIRC command constants, `_IOC_DIR`, `umove_or_printaddr`, `lirc_features`, and `lirc_modes` xlats.
Control flow: accepts a whitelist of LIRC get/set commands; read ioctls are decoded on exit, write ioctls on entry; prints feature flags, mode names, hexadecimal transmitter masks, or unsigned values.
State and persistence behavior: stateless tracee-memory read. Dependencies and integration points: called by the central ioctl dispatcher.
Risks: direction-sensitive timing is important because read commands populate the argument on exit. Test signals: LIRC ioctl fixtures for get features, get/set modes, masks, and unknown commands.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/lirc_ioctl.c -->
