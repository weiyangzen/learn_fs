# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/usb/clients/audio/usb_mixer.h

## Purpose
USB audio mixer registration and request definitions shared with audio streaming/control code.

## Main Interfaces
- Defines `USB_AUDIO_MIXER_REGISTRATION`.
- Defines `usb_audio_formats_t`, `usb_audio_play_req_t`, and `usb_as_registration_t`.
- Defines maximum format count `USB_AS_N_FORMATS`.
- Defines mixer/audio operation commands such as setup, teardown, start/stop/pause play, start/stop record, set format, and set sample frequency.
- Defines control-change IDs for volume, balance, mute, bass, and treble.

## Dependencies And Relationships
Used by USB audio components to register streaming capabilities and issue control/playback requests through the mixer/audio framework integration.

## Research Notes
The header is a compact contract between USB audio streaming and mixer control code rather than a USB wire-format header.
