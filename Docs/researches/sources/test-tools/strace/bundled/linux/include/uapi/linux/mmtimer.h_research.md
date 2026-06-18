# sources/test-tools/strace/bundled/linux/include/uapi/linux/mmtimer.h

Purpose: defines the ioctl ABI for Intel/SGI multimedia timer devices, exposing timer resolution, frequency, counter width, mmap availability, offset, and current counter value.

Important APIs/types/functions: constants include `MMTIMER_IOCTL_BASE`, `MMTIMER_GETOFFSET`, `MMTIMER_GETRES`, `MMTIMER_GETFREQ`, `MMTIMER_GETBITS`, `MMTIMER_MMAPAVAIL`, and `MMTIMER_GETCOUNTER`.

Control flow: userspace opens the timer device, checks whether registers can be mmapped, reads frequency/resolution/bits, and either mmaps registers or calls `MMTIMER_GETCOUNTER` to read current timer value.

State/persistence behavior: all exported ioctls are read-only observations of hardware/device capability and counter state. The counter itself advances independently in hardware.

Dependencies/integration: relies on Linux `_IO/_IOR` ioctl encoding and unsigned long result sizes. Integrates with legacy high-resolution timing consumers and device-driver mmap support.

Risks and test signals: optional vs required ioctls and unsigned-long size differences are the main risks. Tests should decode all commands, validate pointer result formatting, and cover mmap-available versus ioctl-only devices.
