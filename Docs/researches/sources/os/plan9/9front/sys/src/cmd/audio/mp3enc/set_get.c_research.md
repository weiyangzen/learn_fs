# File Research: sources/os/plan9/9front/sys/src/cmd/audio/mp3enc/set_get.c

This file contains part of the `lame_global_flags` setter/getter API plus many forward declarations for additional public settings.

Implemented setters/getters:
- Input stream:
  - `lame_set_num_samples()`, `lame_get_num_samples()`
  - `lame_set_in_samplerate()`, `lame_get_in_samplerate()`
  - `lame_set_num_channels()`, `lame_get_num_channels()`
  - `lame_set_scale()`, `lame_get_scale()`
  - `lame_set_out_samplerate()`, `lame_get_out_samplerate()`
- General controls:
  - `lame_set_analysis()`, `lame_get_analysis()`
  - `lame_set_bWriteVbrTag()`, `lame_get_bWriteVbrTag()`
  - `lame_set_disable_waveheader()`, `lame_get_disable_waveheader()`
  - `lame_set_decode_only()`, `lame_get_decode_only()`
  - `lame_set_ogg()`, `lame_get_ogg()`
  - `lame_set_quality()`, `lame_get_quality()`
  - `lame_set_mode()`, `lame_get_mode()`
  - `lame_set_mode_automs()`, `lame_get_mode_automs()`
- Message callback setters:
  - `lame_set_errorf()`
  - `lame_set_debugf()`
  - `lame_set_msgf()`

Declared but not implemented in this file:
- Many settings for force-MS, free-format, bitrate/compression ratio, frame flags, reservoir, experimental options, VBR controls, filters, ATH options, psychoacoustic flags, and internal read-only values.

Validation behavior:
- Boolean-like fields generally reject values outside `0..1`.
- `lame_set_num_channels()` rejects zero and values above two.
- `lame_set_mode()` rejects modes outside the `MPEG_mode` enum range.
- Getter assertions document expected normalized values.

Dependencies:
- Includes `lame.h` for public encoder structures and enums.

Integration:
- Intended as the public C API layer for configuring `lame_global_flags`.
- The implemented functions directly mutate fields in `lame_global_flags`; derived validation and adjustment happen later in `lame_init_params()`.

Risks and edge cases:
- Large portions of this `.c` file are only prototypes, not implementations. If matching implementations are absent elsewhere, the public API is incomplete.
- Many setters perform minimal validation and allow values later clamped or interpreted by initialization.
- Assertions in getters catch invalid state only when assertions are enabled.
- Callback setters store raw function pointers without null checks, which may be intentional for disabling callbacks.
