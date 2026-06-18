# sources/storage-engines/foundationdb/contrib/linenoise/include/linenoise/linenoise.h

## Purpose
`linenoise.h` declares the public C API for the vendored linenoise line editor used by interactive command-line tools.

## Important APIs, Types, And Functions
`linenoiseCompletions` stores completion strings. Callback types are `linenoiseCompletionCallback`, `linenoiseHintsCallback`, and `linenoiseFreeHintsCallback`. Public functions configure callbacks, add completions, read a line with `linenoise(prompt)`, free returned memory, manage history, clear the screen, enable multiline mode, and print key codes.

## Control Flow
The header has declarations only. Runtime behavior is implemented in `linenoise.c`.

## State And Persistence Behavior
The API exposes global editor configuration and history behavior. Returned lines and completions use heap allocation and must be freed by the caller or by linenoise completion cleanup.

## Dependencies And Integration Points
It includes `<stddef.h>` and is C++ compatible through `extern "C"`. It is the public include path for the `linenoise` CMake target.

## Risks And Edge Cases
The API is global rather than context-based, so callbacks, multiline mode, and history are process-wide. Callers must use `linenoiseFree` or compatible `free` for returned buffers. Callback contracts are not strongly typed beyond raw pointers.

## Test Signals
Compile tests should include the header from C and C++. Behavioral tests should exercise completion callback registration, hint callback/free callback, history save/load, and non-TTY line reads.
