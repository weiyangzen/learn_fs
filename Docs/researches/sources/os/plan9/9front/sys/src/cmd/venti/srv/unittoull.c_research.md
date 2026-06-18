# File Research: sources/os/plan9/9front/sys/src/cmd/venti/srv/unittoull.c

`unittoull.c` parses unsigned numeric strings with optional `K`, `M`, `G`, or `T` suffixes into `u64int`. It returns all-ones `TWID64` on nil input or trailing garbage.

The helper is used for command-line cache sizes, block sizes, and similar operator-provided quantities. It uses `strtoul`, so callers should treat it as a convenience parser rather than a full overflow-detecting numeric validator.
