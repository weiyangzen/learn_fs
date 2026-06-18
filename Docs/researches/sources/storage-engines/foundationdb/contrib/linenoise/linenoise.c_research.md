# sources/storage-engines/foundationdb/contrib/linenoise/linenoise.c

## Purpose
`linenoise.c` implements a compact POSIX terminal line editor with history, tab completion, hints, single-line and multiline refresh, raw terminal mode, and a non-TTY fallback.

## Important APIs, Types, And Functions
Global configuration includes unsupported terminal names, completion/hint/free callbacks, original termios, raw-mode flags, multiline mode, and history storage. `struct linenoiseState` tracks the current edit buffer, cursor, prompt, terminal columns, multiline rows, and history index. Public APIs include `linenoise`, `linenoiseFree`, `linenoiseSetCompletionCallback`, `linenoiseSetHintsCallback`, `linenoiseSetFreeHintsCallback`, `linenoiseAddCompletion`, `linenoiseHistoryAdd`, `linenoiseHistorySetMaxLen`, `linenoiseHistorySave`, `linenoiseHistoryLoad`, `linenoiseClearScreen`, `linenoiseSetMultiLine`, and `linenoisePrintKeyCodes`.

Internal helpers cover raw mode (`enableRawMode`, `disableRawMode`, `linenoiseAtExit`), terminal sizing (`getCursorPosition`, `getColumns`), completion (`completeLine`, `freeCompletions`), screen refresh (`abuf`, `refreshShowHints`, `refreshSingleLine`, `refreshMultiLine`, `refreshLine`), edit actions (`linenoiseEditInsert`, movement, delete, history navigation), raw input (`linenoiseEdit`, `linenoiseRaw`), and non-TTY input (`linenoiseNoTTY`).

## Control Flow
`linenoise(prompt)` chooses among three modes: unlimited line reading for non-TTY stdin, plain `fgets` for unsupported terminals, or raw interactive editing. Raw editing enables termios raw mode, writes the prompt, adds a temporary empty history entry, reads one byte at a time, dispatches control keys and escape sequences, refreshes the terminal as needed, removes the temporary history entry on enter/EOF, restores terminal mode, prints a newline, and returns a heap copy of the buffer.

Completion invokes the registered callback, cycles through completion candidates on repeated tab, accepts a candidate on other input, or restores the original buffer on escape. History navigation updates the temporary latest history entry before replacing the buffer. Refresh builds ANSI escape sequences in an append buffer to reduce flicker.

## State And Persistence Behavior
Most editor configuration is global process state: callbacks, raw-mode status, multiline mode, history max length, history length, and history entries. `linenoiseHistorySave` persists history to a user-readable/writeable file after temporarily tightening the umask; `linenoiseHistoryLoad` reads lines from a file into memory. `atexit` restores terminal mode and frees history.

## Dependencies And Integration Points
The file depends on POSIX headers and APIs: termios, unistd, ioctl `TIOCGWINSZ`, stat/chmod/umask, read/write, isatty, and stdio allocation functions. It implements the declarations from `linenoise/linenoise.h` and is compiled into the `linenoise` static target for interactive FoundationDB tools.

## Risks And Edge Cases
Global state makes the library non-reentrant and not thread-safe. Raw mode checks `STDIN_FILENO` even when passed a file descriptor. Terminal escape parsing handles a limited set of sequences and reads only a few bytes. Many write errors are ignored because recovery is difficult. Manual allocation and callback ownership require care. History load returns `-1` for missing files despite a comment saying missing files return zero. The library is Unix-specific and lacks Win32 support.

## Test Signals
Unit tests can cover non-TTY input, history add/dedup/max length/save/load, completion list allocation, and edit helper behavior with synthetic `linenoiseState`. Integration tests need pseudo-terminal coverage for raw mode, cursor movement, multiline refresh, hints, ctrl-key handling, unsupported `TERM`, and terminal restoration after errors.
