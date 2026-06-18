# File Research: sources/os/plan9/9front/sys/src/cmd/audio/mp3enc/timestatus.h

This header declares progress-reporting APIs for encoder and decoder command-line status.

Exports:
- `timestatus_klemm(const lame_global_flags *gfp)`
- `timestatus(int samp_rate, int frameNum, int totalframes, int framesize)`
- `timestatus_finish(void)`
- `decoder_progress(const lame_global_flags *gfp, const mp3data_struct *)`
- `decoder_progress_finish(const lame_global_flags *gfp)`

Dependencies:
- Requires `lame_global_flags` and `mp3data_struct` to be declared before inclusion.

Integration:
- Used by command-line encoding/decoding paths to display progress.
- Implemented by `timestatus.c`.

Risks and edge cases:
- Does not include `lame.h`, so include order matters.
- The decoder finish function accepts `gfp` but the implementation does not use it.
