# File Research: sources/os/plan9/9front/sys/src/9/port/audioif.h

Portable audio device interface definitions.

Key contents:
- `Audio` device object with device name, controller/mixer pointers, open refs, read/write/close callbacks, volume callbacks, control/status callbacks, buffered callback, delay/speed fields, controller number, and linked-list pointer.
- Volume channel/type enum values for left, right, stereo, and absolute, with `Mono` aliased to `Left`.
- `Volume` descriptor containing name, register, range, type, and capability bits.
- Prototypes for `addaudiocard`, `genaudiovolread`, and `genaudiovolwrite`.

Notable dependencies:
- Kernel `Ref` and audio-device implementations that provide the callback functions.

Research notes:
- This is an interface header only; policy and device behavior live in individual audio drivers.
