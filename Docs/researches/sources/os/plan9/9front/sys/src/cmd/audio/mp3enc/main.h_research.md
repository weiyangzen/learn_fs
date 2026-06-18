# File Research: sources/os/plan9/9front/sys/src/cmd/audio/mp3enc/main.h

## Scope
Shared frontend globals and small utility macros for `main.c` and `parse.c`.

## APIs and Data
Includes `get_audio.h`, defines `MAX_NAME_SIZE`, declares globals `input_format`, `swapbytes`, `silent`, `brhist`, `mp3_delay`, `mp3_delay_set`, and `update_interval`. Defines `Min`, `Max`, and `MAX_U_32_NUM`.

## Dependencies
Depends on `sound_file_format` from `get_audio.h`.

## Risks and Notes
The header comment calls the global sharing “ugly”; `parse.c` owns the definitions. There is no include guard.
