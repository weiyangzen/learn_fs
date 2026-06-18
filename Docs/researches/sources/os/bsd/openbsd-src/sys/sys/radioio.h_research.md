# File Research: sources/os/bsd/openbsd-src/sys/sys/radioio.h

Defines radio tuner ioctl ABI.

Key contents:
- FM and TV channel bounds plus intermediate frequency constant.
- `struct radio_info`: mute, volume, stereo, reference frequency, lock sensitivity, frequency, capabilities, status info, tuner mode, channel, and channel set.
- Capability bits for stereo/signal detection, mono, hardware search/AFC, reference frequency, lock sensitivity, reserved fields, and card type.
- Status bits for stereo and signal.
- Tuner mode bits for radio and TV.
- Ioctls `RIOCGINFO`, `RIOCSINFO`, and `RIOCSSRCH`.

Risk notes:
- The ABI mixes settings and hardware capabilities in one structure; drivers must preserve unsupported fields correctly.
