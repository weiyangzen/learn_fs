# File Research: sources/os/plan9/9front/sys/src/cmd/audio/mp3enc/lame.h

## Scope
Public LAME API header for the bundled `mp3enc` encoder/decoder interface. It defines user-visible configuration, encoder lifecycle calls, encode/decode entry points, ID3 tag functions, and exported MPEG lookup tables.

## APIs and Data
Defines `vbr_mode`, `MPEG_mode`, `lame_global_flags`, and alias `lame_t`. `lame_global_flags` includes input description, output controls, VBR settings, filters, psychoacoustic tuning, reporting callbacks, visible internal counters, and VBR tag bookkeeping. API coverage includes `lame_init`, parameter setters/getters, `lame_init_params`, version getters, `lame_encode_buffer*`, `lame_encode_flush`, `lame_close`, obsolete `lame_encode_finish`, mpglib-backed decode calls, ID3 tag setters, and `bitrate_table`/`samplerate_table`.

## Dependencies
Requires `stdio.h` and `stdarg.h`; C++ callers get `extern "C"`. Optional declarations are gated by `KLEMM_44`.

## Risks and Notes
The public struct exposes many internal fields and comments warn callers not to modify some of them. Several APIs are obsolete or conditionally available. Decode APIs depend on mpglib being compiled in. `LAME_MAXMP3BUFFER` is marked obsolete but still used by the frontend.
