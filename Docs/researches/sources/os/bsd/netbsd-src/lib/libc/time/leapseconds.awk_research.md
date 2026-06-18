# File Research: sources/os/bsd/netbsd-src/lib/libc/time/leapseconds.awk

## Purpose
Generates tzdb `leapseconds` data from `leap-seconds.list`.

## Key Elements
Prints a fixed explanatory header, skips blanks/comments, tracks previous TAI-UTC offset, detects positive or negative leap corrections, maps January/July effective dates to previous December/June end dates, and emits `Leap` lines marked stationary UTC.

## Dependencies
Uses awk and expects input fields from public-domain `leap-seconds.list`.

## Behavior/Risks
Output depends on month names and field positions in the source list. It ignores the first observed offset and emits changes only when a previous offset exists.
