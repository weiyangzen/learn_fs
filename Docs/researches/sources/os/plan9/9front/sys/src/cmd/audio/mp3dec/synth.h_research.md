# File Research: sources/os/plan9/9front/sys/src/cmd/audio/mp3dec/synth.h

This header declares libmad's PCM output and synthesis-state API.

Key declarations:
- `struct mad_pcm`: samplerate, channel count, per-channel sample count, and fixed-point PCM samples `[2][1152]`.
- `struct mad_synth`: polyphase filterbank history, current phase, and embedded `struct mad_pcm`.
- Channel selector enums for single-channel, dual-channel, and stereo output.
- Public functions `mad_synth_init()`, `mad_synth_mute()`, and `mad_synth_frame()`.
- `mad_synth_finish(synth)` is a no-op macro.

Dependencies and integration:
- Includes `fixed.h` for `mad_fixed_t`.
- Includes `frame.h` for `struct mad_frame`.
- Implemented by `synth.c`.
- Consumed by decoder front ends that need PCM output after frame decoding.

Data model:
- `samples[2][1152]` matches MPEG Layer III's maximum PCM samples per channel per frame.
- `filter[2][2][2][16][8]` stores the channel, even/odd, phase parity, synthesis slot, and vector state needed by the polyphase filterbank.

Risks and edge cases:
- The header exposes fixed-size arrays, so callers must respect `pcm.channels` and `pcm.length` rather than assuming every slot is valid.
- The finish macro means there is no dynamic resource cleanup for this object.
