# File Research: sources/os/plan9/9front/sys/src/cmd/seq.c

Purpose: Prints numeric sequences.

Behavior:
- Usage: `seq [-fformat] [-w] [first [incr]] last`.
- Defaults: first 1, increment 1.
- `-f` supplies a `sprint` format, with newline appended if missing.
- `-w` builds constant-width decimal output and zero-fills leading spaces.
- Supports positive and negative increments, rejects zero increment.

Risks:
- Floating-point loop accumulation can drift for fractional increments.
- Format buffer for `-f` is 4096 bytes but user format is not otherwise validated.
