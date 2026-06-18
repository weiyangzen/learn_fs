# File Research: sources/os/bsd/dragonflybsd/sys/sys/soundcard.h

This large header defines the OSS/VoxWare/FreeBSD soundcard compatibility ABI: audio formats, sound device IDs, DSP/sequencer/mixer/MIDI/coprocessor ioctls, event formats, convenience sequencer macros, and OSSv4 metadata structures.

Key responsibilities:
- Defines `SOUND_VERSION` and legacy VoxWare marker.
- Defines legacy sound card IDs such as AdLib, SoundBlaster, GUS, MPU401, MSS, OPL, and related devices.
- Defines newer FreeBSD audio ioctls:
  - `AIONWRITE`
  - `AIOGSIZE`/`AIOSSIZE`
  - `AIOGFMT`/`AIOSFMT`
  - mixer/sync/capability ioctls
- Defines audio format bitmasks:
  - mu-law, A-law, ADPCM, signed/unsigned 8/16/24/32-bit, MPEG, AC3
  - native-endian and opposite-endian aliases
  - stereo, weird hardware, full-duplex capabilities
- Defines `snd_chan_param`, `snd_mix_param`, `snd_sync_parm`, and `snd_capabilities`.
- Defines legacy `/dev/sequencer` ioctl set, timer ioctls, and sequence event records.
- Defines patch/sample upload structures:
  - `patch_info`
  - `sysex_info`
  - `sbi_instrument`
  - `patmgr_info`
- Defines patch manager status, command, event, and data payload constants.
- Defines sequencer event codes, MIDI controller constants, MIDI event types, timer event types, local events, and multiple compatibility aliases.
- Defines synth, timer, and MIDI info structures:
  - `synth_info`
  - `sound_timer_info`
  - `midi_info`
  - `mpu_command_rec`
- Defines `/dev/dsp` and `/dev/audio` ioctls for reset/sync/speed/stereo/format/buffer/fragments/nonblock/caps/triggers/pointers/mmap/syncro/duplex/delay.
- Defines `audio_buf_info`, `count_info`, and buffer mapping structures.
- Defines PCM/DSP capability bits and compatibility aliases between `PCM_CAP_*` and `DSP_CAP_*`.
- Defines coprocessor buffer/debug/message structures and coprocessor ioctls.
- Defines legacy mixer device indexes, names, labels, masks, read/write ioctl macros, and `mixer_info`.
- Defines sequencer convenience macros for building output buffers and events:
  - buffer declaration/use
  - patch loading
  - MIDI voice/common/sysex events
  - controller/bender/timer/local/audio events
- Defines ioctl alias names such as `SOUND_PCM_WRITE_BITS`, `SOUND_PCM_GETOSPACE`, etc.
- Defines OSSv4 additions:
  - long-name/label/devnode typedefs
  - `audio_errinfo`
  - sync groups
  - cooked mode, silence/skip, input/output halt, low-water, 64-bit counters
  - recording/playback target routing controls
  - channel ordering and peak metering
  - channel binding flags
  - `oss_sysinfo`, `oss_mixext`, `oss_mixer_value`, `oss_mixer_enuminfo`
  - `oss_audioinfo`, `oss_mixerinfo`, `oss_midi_info`, `oss_card_info`
  - system/mixer/audio/MIDI/card/engine info ioctls
  - song/name/label ioctls

Important invariants:
- The file warns that ioctl commands and ABI types must not be changed incompatibly without coordinating with OSS upstream.
- Mixer IDs use a bitmask space where bit 31 is reserved.
- Sequencer level-1 events are 4 bytes; many level-2 and extended events are 8 bytes.
- `SEQ_FULLSIZE` patch/sample uploads must be written as exactly one write call without mixed events.
- OSSv4 `SOUND_VERSION` is redefined to `0x040000` if already defined.
- Many structs contain large filler arrays for ABI extension without changing size.

Research notes:
- This is primarily compatibility ABI surface rather than DragonFly-specific implementation.
- It intentionally preserves obsolete names and misspellings, for example `SNDCTL_SEQ_TRESHOLD`, to match historical applications.
