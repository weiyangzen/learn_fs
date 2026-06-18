# File Research: sources/os/bsd/freebsd-src/sys/sys/soundcard.h

## Purpose
`soundcard.h` defines FreeBSD's OSS/VoxWare-compatible public sound device ABI: audio formats, mixer controls, DSP ioctls, MIDI/sequencer events, patch loading structures, and OSSv4 information/control structures.

## Main Interfaces
- FreeBSD-specific audio ioctls include `AIONWRITE`, `AIOGSIZE`, `AIOSSIZE`, `AIOGFMT`, `AIOSFMT`, `AIOGMIX`, `AIOSMIX`, `AIOSTOP`, `AIOSYNC`, and `AIOGCAP`.
- Audio format masks cover mu-law, A-law, IMA ADPCM, signed/unsigned 8/16/24/32-bit PCM, MPEG, AC3, float, native/opposite endian aliases, stereo, full-duplex, and hardware format constraints.
- Classic OSS/VoxWare ioctls cover `/dev/sequencer`, timer control, MIDI, `/dev/dsp`, coprocessor loading/debug messaging, and `/dev/mixer`.
- Defines ABI structs such as `snd_chan_param`, `snd_mix_param`, `snd_capabilities`, `patch_info`, `sysex_info`, `patmgr_info`, `synth_info`, `midi_info`, `audio_buf_info`, `count_info`, `copr_buffer`, `mixer_info`, `oss_sysinfo`, `oss_audioinfo`, `oss_mixerinfo`, `oss_midi_info`, and `oss_card_info`.
- Provides userland sequencer convenience macros for buffering and emitting MIDI voice, channel, sysex, timer, local, and patch events.

## Implementation Notes
The header explicitly warns that ioctl command numbers and types must preserve OSS compatibility. Many definitions are historical aliases or obsolete compatibility names, but remain part of the ABI. Mixer devices use numeric channel IDs and bitmasks, with read/write ioctl constructors. OSSv4 additions extend device discovery, mixer extension metadata, sync groups, cooked mode, peak meters, channel ordering, and global song/name/label controls.

## Dependencies and Constraints
Includes `sys/types.h`, `machine/endian.h`, and `sys/ioccom.h` when ioctl macros are not already present. Consumers depend on exact struct layout, ioctl numbers, endian aliases, and legacy macro names.
