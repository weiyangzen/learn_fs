# File Research: sources/os/bsd/netbsd-src/lib/libedit/readline/readline.h

## Purpose
Public readline/history compatibility header provided by libedit.

## Main Declarations
Defines readline-compatible callback typedefs, `HIST_ENTRY`, `HISTORY_STATE`, `KEYMAP_ENTRY`, `Keymap`, key constants, readline version/state macros, prompt ignore markers, and exported global variables.

Declares public functions for:
- Line input and prompt management.
- History manipulation, persistence, search, tokenization, and expansion.
- Completion functions and match display.
- Key binding and keymap compatibility.
- Signal/terminal/display helpers.
- A set of explicitly-noted not-implemented or stubbed functions.

## Integration
Installed as both `readline/readline.h` and `readline/history.h` by the adjacent Makefile. Implemented primarily by `readline.c`, backed by libedit's native `histedit.h` API.

## Risks And Notes
This header aims at source compatibility, not full GNU Readline behavioral identity. Callers using advanced keymap or signal APIs may hit stubbed or partial behavior.
