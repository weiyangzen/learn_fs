# File Research: sources/os/plan9/9front/sys/src/cmd/ip/ppp/thwack.c

This is the Thwack encoder. It implements a sliding-window LZ-style compressor with custom variable-length coding for literals, match lengths, and offsets.

`thwackinit` resets the encoder window, per-slot hash tables, block metadata, and retained `Block` references. `thwackcleanup` frees retained blocks. `thwackack` marks sequence blocks acknowledged by the decoder, enabling them as usable history for future compression.

`thwmatch` searches current and acknowledged history blocks through per-block hash tables keyed by a three-byte rolling value. Matches are encoded as length plus backward offset over a compound history assembled from the current block and acknowledged previous blocks.

`thwack` is the main compressor. It rejects oversized or too-small source blocks, inserts the source block into the encoder window, builds a bounded history list, emits sequence/history mask metadata, then encodes literals and matches. It bails out when output would exceed the destination and `mustadd` is false. It also has a progress heuristic that stops compression if the first half of a block shows poor compression.

The encoder keeps original source `Block` objects in the history window after successful insertion, so ownership is transferred to the encoder until cleanup or window replacement.
