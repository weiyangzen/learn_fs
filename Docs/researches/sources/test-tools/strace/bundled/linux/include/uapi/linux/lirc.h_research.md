# sources/test-tools/strace/bundled/linux/include/uapi/linux/lirc.h

Purpose: defines the Linux infrared remote control ABI for raw/mode2/scancode data, device feature flags, and LIRC ioctl configuration.

Important APIs/types/functions: macros encode/decode `LIRC_MODE2_*` packets, capability bits describe send/receive features, ioctls include `LIRC_GET_FEATURES`, mode getters/setters, carrier/duty/timeout controls, and wideband settings. `struct lirc_scancode` and `enum rc_proto` define decoded scancode records.

Control flow: userspace queries features, selects send/receive modes, configures carrier/timing behavior, reads pulse/space/frequency/timeout/overflow mode2 values or scancode records, and transmits protocol-specific data where supported.

State/persistence behavior: mode and carrier ioctls mutate per-device driver configuration. Timeout reporting and carrier measurement change future event stream contents. Scancode records are transient input data.

Dependencies/integration: depends on Linux types and ioctl macros. Integrates with rc-core protocols, media input devices, and lirc userspace daemons.

Risks and test signals: the upper byte of mode2 values carries packet type, so formatting must mask correctly. Tests should exercise capability flag groups, ioctl numbers, timeout-report toggles, scancode flags, and every `RC_PROTO_*` value.
