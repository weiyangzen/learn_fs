# File Research: sources/os/plan9/9front/sys/src/cmd/audio/oggdec/oggdec.c

Plan 9-adapted Ogg Vorbis decoder command that writes raw audio through `audio/pcmconv`.

Key responsibilities:
- Reads Ogg pages from stdin, validates Vorbis headers, prints comments/stream metadata, and decodes chained streams.
- Converts libvorbis planar float PCM into interleaved float samples.
- Starts or restarts `/bin/audio/pcmconv` whenever sample rate or channel count changes.
- Supports `-s SECONDS` seeking using Ogg granule time and coarse `fseek` adjustment.
- Handles chained bitstreams by resetting stream/decoder state on a new BOS page.

Dependencies:
- Uses libogg/libvorbis, POSIX stdio/fork/pipe APIs, and Plan 9 compatibility headers.
- Depends on `/bin/audio/pcmconv` for conversion to default Plan 9 audio output format.

Research notes:
- The converter subprocess receives float PCM with format string like `f32r44100c2`.
- Seek behavior is heuristic and only applies to seekable stdin.
