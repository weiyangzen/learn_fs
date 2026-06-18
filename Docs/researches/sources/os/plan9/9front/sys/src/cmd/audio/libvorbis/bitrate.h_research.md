# File Research: sources/os/plan9/9front/sys/src/cmd/audio/libvorbis/bitrate.h

## Role

This private libvorbis header defines bitrate manager state/configuration and declares the bitrate management API.

## Main Structures

`bitrate_manager_state` stores runtime state:

- Managed-mode flag.
- Average and min/max reservoirs.
- Target bits per half block.
- Short-per-long scaling.
- Floating packet-blob choice.
- Pending `vorbis_block`.
- Final selected packet-blob index.

`bitrate_manager_info` stores setup configuration:

- Average, min, and max rates.
- Reservoir bit capacity.
- Reservoir bias.
- Slew damping.

## API

Declared functions are:

- `vorbis_bitrate_init`
- `vorbis_bitrate_clear`
- `vorbis_bitrate_managed`
- `vorbis_bitrate_addblock`
- `vorbis_bitrate_flushpacket`

## Integration Notes

The bitrate manager is encode-side only and depends on codec internals plus Ogg packet output semantics.
