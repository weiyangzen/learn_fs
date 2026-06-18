# File Research: sources/os/plan9/9front/sys/src/cmd/audio/mp3enc/parse.c

## Scope
Command-line parsing, usage/help text, presets, file-type detection, and frontend global option state.

## APIs and Behavior
Defines globals declared in `main.h`. Help functions print version, license, usage, short help, long help, bitrate tables, and preset information. Presets map names like `phone`, `fm`, `hifi`, `cd`, and `studio` to resampling, filters, block behavior, mode, CBR, and VBR ranges. `parse_args()` handles GNU-style long options and compact short options, mutating `lame_global_flags`, ID3 state, input format, silence/status settings, byte swapping, decoder delay, and frontend VBR histogram behavior.

## Control Flow
Long options include input type, Ogg/Vorbis, presets, decode, ATH/noise-shaping controls, ID3 fields, filters, ABR/VBR, nspsytune controls, verbosity, version/license/help, and display interval. Short options cover mode, VBR quality, sample rate, bitrate min/max, raw input, byte swap, CRC, mono conversion, filters, experimental toggles, emphasis, copyright/original bits, and help. After parsing, this 9front version forces `silent = 1` and disables VBR tag writing, reflecting stdin/stdout behavior.

## Dependencies
Uses `lame.h`, `brhist.h`, `parse.h`, `main.h`, and `get_audio.h`; calls many LAME setters and ID3 APIs.

## Risks and Notes
Parsing mostly uses `atoi`/`atof` with limited validation. `local_strcasecmp()` passes plain `char` to `tolower`, which can be undefined for negative signed chars. `presets_setup()` accepts prefix matches, so ambiguous prefixes can select the first matching preset. `parse_args()` resets globals on every call, relevant because `main.c` calls it once for `LAMEOPT` and once for argv.
