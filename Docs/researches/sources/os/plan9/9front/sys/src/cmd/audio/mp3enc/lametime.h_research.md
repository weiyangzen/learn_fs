# File Research: sources/os/plan9/9front/sys/src/cmd/audio/mp3enc/lametime.h

## Scope
Header for time/file utility helpers.

## APIs
Declares `GetCPUTime`, `GetRealTime`, `lame_set_stream_binary_mode`, and `lame_get_file_size`.

## Dependencies
Includes `sys/types.h` and `lame.h`, mainly for `FILE` and `off_t`.

## Risks and Notes
Simple guarded header; the binary-mode function is platform-dependent in implementation.
