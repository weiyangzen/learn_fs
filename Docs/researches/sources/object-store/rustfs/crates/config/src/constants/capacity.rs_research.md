# sources/object-store/rustfs/crates/config/src/constants/capacity.rs

## Purpose
Defines environment variable names and defaults for capacity calculation scheduling, sampling, symlink behavior, metrics, and timeout/stall detection.

## Important APIs, types, and functions
Environment constants include scheduled interval, write trigger delay, write frequency threshold, fast update threshold, max files threshold, stat timeout, sample rate, metrics interval, symlink following/depth, dynamic timeout, min/max timeout, and stall timeout. Defaults include 120 s scheduled updates, 5 s write trigger, 5 writes/min threshold, 30 s fast threshold, 200k max files, 3 s stat timeout, sample rate 200, 600 s metrics interval, symlink following disabled, max symlink depth 3, dynamic timeout enabled, 2 s min timeout, 15 s max timeout, and 20 s stall timeout.

## Control flow
No runtime flow; capacity service configuration code imports these constants and parses corresponding env vars.

## State and persistence behavior
Static constants only.

## Dependencies and integration points
Used by capacity/statistics scanners and metrics emitters that need safe defaults for expensive filesystem traversal and sampling.

## Risks and edge cases
Defaults trade accuracy for cost through sampling and thresholds. Following symlinks is disabled by default for safety; if enabled downstream must guard loops and depth. Timeout defaults may be too short on slow or remote filesystems. Env parsing and bounds validation are outside this file.

## Test signals
Unit tests assert exact env var names and default values.
