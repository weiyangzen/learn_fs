# File Research: sources/os/bsd/freebsd-src/sys/sys/sndstat.h

Sound device status ioctl and nvlist schema header.

Key responsibilities:
- Defines `struct sndstioc_nv_arg` for passing packed nvlist buffers through ioctl.
- Defines common nvlist keys for device lists, playback/recording info, provider data, and sound(4)-specific channel/buffer fields.
- Defines maximum user nvlist buffer size `SNDST_UNVLBUF_MAX`.
- Defines ioctls `SNDSTIOC_REFRESH_DEVS`, `SNDSTIOC_GET_DEVS`, `SNDSTIOC_ADD_USER_DEVS`, and `SNDSTIOC_FLUSH_USER_DEVS`.
- Under 32-bit compatibility, defines `sndstioc_nv_arg32` and ioctl type substitutions.

Important patterns:
- The ABI exports structured sound status as packed nvlists rather than fixed C structs.
- Key names are centralized to keep kernel producers and userspace consumers aligned.
- Compatibility handles pointer-size differences in ioctl payloads.

Research relevance:
- Device-status ABI example using nvlists for extensible kernel/userspace reporting.
