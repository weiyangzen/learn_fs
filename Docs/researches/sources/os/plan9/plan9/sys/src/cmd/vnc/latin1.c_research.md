# File Research: sources/os/plan9/plan9/sys/src/cmd/vnc/latin1.c

Plan 9 Latin compose sequence interpreter.

Key responsibilities:
- Builds `latintab[]` from `latin1.h`.
- Supports `Xhhhh` four-hex-digit Unicode input.
- Resolves one-, two-, and three-character compose sequences to runes.
- Returns `-1` for invalid sequence and negative required-length markers when more input is needed.

Important behavior:
- Table assumptions are documented: leader length is one or two, and prefix ordering matters.
- `unicode()` skips initial `X` and parses exactly four hex digits.
- `latin1()` returns `-2`, `-3`, or `-5` to request more keystrokes.

Risks:
- Correct prefix handling depends on table ordering in `latin1.h`.
