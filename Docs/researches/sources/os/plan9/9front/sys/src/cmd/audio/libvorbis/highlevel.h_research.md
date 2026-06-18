# File Research: sources/os/plan9/9front/sys/src/cmd/audio/libvorbis/highlevel.h

Header defining high-level encoder setup structures used by Vorbis encoder setup code.

Important contents:
- `highlevel_byblocktype` stores per-block-type tone mask, tone peak limit, noise bias, and noise companding settings.
- `highlevel_encode_setup` stores user-facing/derived encoder configuration: selected setup, base quality, impulse noise tuning, managed bitrate parameters, block/noise/coupling toggles, stereo point, lowpass, ATH controls, amplitude tracking, trigger setting, and per-block settings.

Integration points:
- Included by `codec_internal.h`.
- Stored as `codec_setup_info.hi`, primarily for `vorbisenc.c` setup flow.

Risk and review signals:
- Declaration-only header; no runtime logic or validation.
- Values are redundant with expanded codec setup and must be synchronized by encoder setup code.

Filesystem relevance:
- No filesystem logic. It is encoder configuration data modeling.
