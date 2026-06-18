# File Research: sources/os/bsd/netbsd-src/sys/sys/audioio.h

## Scope

Defines the public audio and mixer ioctl ABI shared by NetBSD audio drivers and userland.

## APIs And Data Structures

- `audio_prinfo` and `audio_info` describe play/record parameters, buffer sizing, watermarks, pause/error/open/active state, and modes `AUMODE_PLAY`, `AUMODE_RECORD`, `AUMODE_PLAY_ALL`.
- `AUDIO_INITINFO()` initializes `audio_info` fields to all-ones for partial update semantics.
- Defines device identification via `audio_device`, transfer offset reporting via `audio_offset`, and encoding discovery via `audio_encoding`.
- Enumerates audio encodings including u-law, A-law, signed/unsigned linear LE/BE/native, MPEG layers, and AC3.
- `audio_format` describes driver formats: mode, encoding, valid bits, precision, channels, channel mask, supported frequencies, and priority.
- Audio ioctls cover get/set info, drain/flush, offsets, errors, properties, channel selection, and format query/set.
- Mixer ABI includes `mixer_level`, `mixer_devinfo`, `mixer_ctrl`, mixer type constants, and mixer read/write/devinfo ioctls.
- Provides canonical mixer device, class, and encoding names.

## Dependencies

- Includes `sys/types.h`, `sys/ioccom.h`, and userland `string.h` for `AUDIO_INITINFO`.

## Risks And Invariants

- Structure layout is an ABI; field size/order changes affect userland.
- `audio_format` comments constrain validbits, precision, channels, and frequency_type interpretation.
- Native-endian encoding aliases are kernel-only.
