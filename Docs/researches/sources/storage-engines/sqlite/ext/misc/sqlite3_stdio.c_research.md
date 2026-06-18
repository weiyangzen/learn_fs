# sources/storage-engines/sqlite/ext/misc/sqlite3_stdio.c

## Purpose
Implements Windows-only UTF-8 aware stdio wrappers declared by `sqlite3_stdio.h`. On non-Windows platforms the file compiles to a no-op.

## Important APIs, Types, And Functions
Exports `sqlite3_fopen`, `sqlite3_popen`, `sqlite3_fgets`, `sqlite3_fputs`, `sqlite3_fprintf`, `sqlite3_vfprintf`, and `sqlite3_fsetmode`. Internal helpers include `UseBinaryWText()` and `piecemealOutput()`. Compile-time options include `SQLITE_U8TEXT_ONLY`, `SQLITE_U8TEXT_STDIO`, and `SQLITE_USE_W32_FOR_CONSOLE_IO`.

## Control Flow
File and process open wrappers convert UTF-8 paths/commands and modes to UTF-16 and call `_wfopen()` or `_wpopen()`. Input from console-like streams reads UTF-16 with either `ReadConsoleW()` or `_O_WTEXT`/`fgetws()`, then converts to UTF-8. Output to console-like streams converts UTF-8 to UTF-16 and writes through `WriteConsoleW()` or `_O_U8TEXT`; simulated binary mode emits ASCII bytes in binary/text mode and switches for non-ASCII segments. Non-console streams use ordinary C stdio.

## State And Persistence Behavior
No persistent data is stored. Two process-global flags, `simBinaryStdout` and `simBinaryOther`, remember simulated binary mode for output streams after `sqlite3_fsetmode()`.

## Dependencies And Integration Points
Depends on Windows APIs, Microsoft CRT mode functions, SQLite memory/formatting APIs, and stdio. It supports CLI and utility code that wants UTF-8 behavior without sprinkling Windows-specific code throughout callers.

## Risks And Edge Cases
The implementation is Windows-specific and relies on CRT mode changes that are process/file-descriptor state. Return values for the wide-output path are approximations rather than exact C stdio semantics. Console detection differs under `SQLITE_U8TEXT_ONLY`, `SQLITE_U8TEXT_STDIO`, and default modes. Allocation or conversion failures generally return null/zero rather than rich diagnostics.

## Test Signals
Windows tests should cover UTF-8 filenames, popen commands, console and redirected input/output, ASCII-only binary output without CRLF translation, non-ASCII rendering, `sqlite3_fsetmode()` transitions, and both Win32 console API and CRT paths.
