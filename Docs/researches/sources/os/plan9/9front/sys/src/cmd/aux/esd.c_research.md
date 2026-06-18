# File Research: sources/os/plan9/9front/sys/src/cmd/aux/esd.c

Role: Partial Enlightened Sound Daemon protocol shim for 9front audio.

Protocol behavior:
- Reads ESD handshake, detects endian mode, then handles ESD operation codes in a loop.
- Stream playback opens `/dev/audio` for writing and execs `/bin/audio/pcmconv -i <format>`.
- Stream monitor opens `/dev/audio` for reading and execs `pcmconv -o <format>`.
- Sample cache consumes input through `pcmconv -l len` to `/dev/null` and returns the supplied sample id.
- Server-info requests return fixed version/rate/format values.

Format handling:
- `pcmfmt` maps ESD format bits to Plan 9 pcmconv format strings with sample size, channels, and rate.

Limitations:
- Many sample operations are acknowledged but not actually cached or replayed.
- Intended to be run behind `aux/listen1` on TCP port 16001.
