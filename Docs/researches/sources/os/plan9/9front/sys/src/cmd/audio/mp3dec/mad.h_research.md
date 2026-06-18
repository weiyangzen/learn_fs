# File Research: sources/os/plan9/9front/sys/src/cmd/audio/mp3dec/mad.h

This is an aggregated public libmad header. It combines version definitions, fixed-point arithmetic declarations/macros, bit pointer APIs, timer declarations, stream declarations, frame declarations, synthesis declarations, and decoder declarations into one include file. `main.c` includes this single header instead of including each subsystem header separately.

It identifies libmad version `0.15.1 (beta)`, defines fixed-point types and architecture-specific multiplication paths, declares `struct mad_bitptr`, `mad_timer_t`, `struct mad_stream`, `struct mad_header`, `struct mad_frame`, `struct mad_pcm`, `struct mad_synth`, and `struct mad_decoder`, plus their public functions and control macros. It also hardcodes `FPM_INTEL` and size macros near the top, making this copy configuration-specific.

Compared with the separate local headers, `mad.h` includes timer and synth public declarations not otherwise in this file list. It is the frontend-facing API surface for the Plan 9 player and mirrors upstream libmad's consolidated include model.
