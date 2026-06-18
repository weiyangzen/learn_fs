# File Research: sources/os/plan9/9front/sys/src/cmd/audio/mp3enc/reservoir.h

This header declares the MP3 bit reservoir API.

Exports:
- `ResvFrameBegin(...)`
- `ResvMaxBits(...)`
- `ResvAdjust(...)`
- `ResvFrameEnd(...)`

Dependencies:
- Relies on types from headers included before it, especially `lame_global_flags`, `lame_internal_flags`, `III_side_info_t`, and `gr_info`.

Integration:
- Included by quantization modules to allocate and reconcile per-frame/per-granule bit budgets.
- Implemented by `reservoir.c`.

Risks and edge cases:
- The header does not include the type-defining headers it needs, so include order matters.
- `ResvMaxBits()` names its fourth pointer `max_bits` in the declaration, while the implementation uses it as `extra_bits`; this is a documentation/API clarity mismatch.
