# File Research: sources/os/plan9/9front/sys/src/cmd/audio/zuke/zuke.c

Graphical Plan 9 audio playlist player for zuke playlists.

Key responsibilities:
- Parses playlists from stdin into in-memory `Meta` records backed by one raw buffer.
- Draws playlist rows, columns, scrollbar, seek bar, volume, replaygain/shuffle/repeat status, current track highlighting, and cover art.
- Manages `/dev/audio` output, `/dev/volume` changes, and audio open/close locking.
- Starts decoder subprocesses like `/bin/audio/mp3dec`, `/bin/audio/oggdec`, etc., or `/bin/play` for generic/URL playback.
- Handles ICY HTTP streams through `icyget()` and live title updates.
- Supports preloading the next player, replaygain track/album modes, repeat-one, shuffle, keyboard/mouse navigation, seeking, searching, and plumb messages.
- Loads embedded or sidecar cover art through `audio/readtags -i`, `jpg`, `png`, and `resample`.
- Emits current-track notifications to stdout when stdout is not `/dev/cons`.

Dependencies:
- Uses Plan 9 draw/mouse/keyboard/plumb/thread libraries, `plist.h`, `icy.h`, audio decoder commands, image decoders, `/dev/audio`, and `/dev/volume`.

Research notes:
- Playback is subprocess-based; zuke itself reads decoded PCM from pipes and writes to `/dev/audio`.
- Shuffle builds a deterministic-looking permutation using an LCG over a power-of-two mask.
- The UI redraw path caches a backing image and coalesces redraw requests through a channel.
