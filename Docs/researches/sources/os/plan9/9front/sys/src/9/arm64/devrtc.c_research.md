# File Research: sources/os/plan9/9front/sys/src/9/arm64/devrtc.c

Minimal PL031 RTC device driver exposed as `#r/rtc`.

Key behavior:
- Maps RTC registers at `VIRTIO + 0x01010000`.
- Exposes a directory with one `rtc` file.
- Reads the current time directly from the first RTC register.
- Allows read access to all users and denies writes except that non-eve write opens are rejected earlier.

Dependencies:
- Uses Plan 9 device table helpers, `readnum`, and standard error handling.

Research notes:
- The write method always returns `Eperm`; this is a read-only RTC interface in practice.
