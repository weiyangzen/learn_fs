# File Research: sources/os/plan9/9front/sys/src/cmd/audio/mp3enc/main.c

## Scope
Command-line frontend for encoding audio to MP3, with optional decode mode.

## Entry Points
`parse_args_from_string()` tokenizes `LAMEOPT` by spaces and passes synthetic argv to `parse_args()`. `main()` initializes LAME, parses environment and command-line options, opens input/output, initializes encoder parameters, loops through input audio, encodes with `lame_encode_buffer`, writes MP3 bytes, flushes, writes VBR tags, closes LAME/output, and closes input.

## Control Flow
Input and output paths are initialized as `"-"`, so this 9front frontend is stream-oriented by default. Decode mode calls `lame_decoder()` with either user-specified MP3 delay or encoder delay. Encode mode reads 1152-sample channel buffers via `get_audio()`, optionally updates status/histogram displays, encodes, writes output, then flushes and finishes status.

## Dependencies
Uses `lame.h`, `brhist.h`, `parse.h`, `main.h`, `get_audio.h`, and `timestatus.h`.

## Risks and Notes
`parse_args_from_string()` is explicitly “quick & dirty”: it splits only on spaces, has a fixed 128-argument array, and does not handle quoting. Several status `fprintf` branches are disabled with `if (0)`.
