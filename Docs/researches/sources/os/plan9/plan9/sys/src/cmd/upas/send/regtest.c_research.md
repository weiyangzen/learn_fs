# File Research: sources/os/plan9/plan9/sys/src/cmd/upas/send/regtest.c

## Purpose
Interactive regexp test utility.

## Behavior
Prompts for a regexp, compiles it, then prompts for lines and prints `yes` or `no` depending on `regexec` result. Empty regexp input exits; empty line input returns to regexp prompt.

## Dependencies
Plan 9 regexp and `Biobuf`.

## Risks / Notes
No handling for `regcomp` failure before `regexec`.
