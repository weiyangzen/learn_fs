# sources/sync-backup/kopia/repo/splitter/splitter_buzhash32.go

Purpose: implements content-defined chunking with a 32-bit BuzHash rolling hash.

Important APIs/types/functions: `buzhash32Splitter` tracks rolling hash, mask, byte count, minimum size, and maximum size. Methods implement `Close`, `Reset`, `NextSplitPoint`, and `MaxSegmentSize`. `newBuzHash32SplitterFactory(avgSize)` creates configured splitters.

Control flow: `NextSplitPoint` skips split checks until roughly half the average size while still rolling the last sliding-window bytes, then scans until max size for `Sum32()&mask == 0`, resetting count and returning consumed bytes at split. If max size is reached without a hash hit, it forces a split.

State and persistence behavior: splitter state is in-memory rolling hash/count. Reset seeds the rolling hash with a zero sliding window for deterministic initial behavior.

Dependencies/integration: depends on `github.com/chmduquesne/rollinghash/buzhash32`, shared window/size constants, and splitter factory registration in `splitter.go`.

Risks: comments note avoiding interface dispatch for performance. Off-by-one behavior around `minSize - count - 1` and max-size forced splits directly affects chunk boundaries and dedup. Average size must be a power of two for the mask logic.

Test signals: splitter stability tests assert exact split count, average, min, and max for multiple BuzHash sizes and input feeding modes.
