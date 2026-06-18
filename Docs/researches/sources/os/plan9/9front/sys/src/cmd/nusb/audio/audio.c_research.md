# File Research: sources/os/plan9/9front/sys/src/cmd/nusb/audio/audio.c

USB audio class driver exposing audio endpoints and control files.

Key elements:
- Supports USB Audio 1.0 and 2.0 descriptor parsing.
- Finds audio control and streaming interfaces, IADs, terminals, clock sources, stream alt settings, isochronous endpoints, format descriptors, and sample-rate ranges.
- `Aconf` extends `Pcmdesc` with endpoint, sample size, terminal, frequency ranges, zero-bandwidth alt setting, and Audio 2 clock ID.
- `setupep` chooses the best matching alt setting for a requested PCM format, sets zero-bandwidth first, sets alt, sets clock, opens endpoint, and programs endpoint device controls.
- Discovers feature-unit controls for mute, volume, bass, mid, treble, AGC, bass boost, and loudness.
- Exposes synthetic files `audioctlU<hname>`, `audiostatU<hname>`, and `volumeU<hname>` through a USB share service.
- `fsread` reports stream on/off state, supported formats, current formats, delay, and control values.
- `fswrite` handles stream on/off, output/input format changes, speed, delay, and feature control changes.

Notable behavior:
- Audio format preference chooses exact matches when possible and otherwise closest/best candidates.
- Audio 2 sample-rate control uses `RANGE`; Audio 1 uses endpoint `SET_CUR/GET_CUR`.
- Volume-like controls are converted between user 0-100 values and hardware min/max/resolution.
- Silence is represented by `0x8000` for 16-bit volume controls.

Risks and quirks:
- `fswrite` initializes `c = epout->aux` before verifying `epout` is non-nil; input-only devices may be sensitive here.
- Some clock-setting failures are ignored because devices do not always require or support them.
- Only the first input and first output endpoint are selected.
