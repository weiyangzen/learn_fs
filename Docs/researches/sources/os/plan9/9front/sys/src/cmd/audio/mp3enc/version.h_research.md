# File Research: sources/os/plan9/9front/sys/src/cmd/audio/mp3enc/version.h

LAME version macro header and version API declarations.

Key contents:
- Defines LAME URL and version components: LAME 3.88 beta 1, PSY 0.85, and mp3x 0.82.
- Declares full/short LAME version, psychoacoustic version, mp3x version, URL, and numerical version functions.

Dependencies:
- Requires `lame_version_t` from `lame.h`.

Research notes:
- This is static version metadata used by `version.c` and callers embedding/reporting the encoder version.
