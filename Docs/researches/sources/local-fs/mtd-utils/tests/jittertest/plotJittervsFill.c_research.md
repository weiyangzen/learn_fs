# File Research: sources/local-fs/mtd-utils/tests/jittertest/plotJittervsFill.c

## Purpose
Extracts high-jitter samples from `JitterTest` logs and pairs them with subsequent filesystem fill percentages.

## Key Elements
Parses `-f/--file`, `-t/--jitter_threshold`, `-d`, help, and version. Scans lines for jitter values in `ms`, saves values exceeding threshold, waits for later `df` percentage lines, then emits `percent jitter` pairs to stderr, optionally prefixed by source line number.

## Dependencies
Uses stdio/string parsing only.

## Behavior/Risks
Parsing assumes specific `JitterTest` and `df` text formats. Stores only 1000 pending jitter samples before a percent line and drops excess.
