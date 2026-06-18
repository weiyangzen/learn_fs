# sources/storage-engines/sqlite/tool/winmain.c

## Purpose
`winmain.c` provides a Windows Unicode command-line entry point that converts `wchar_t**` arguments to UTF-8 and calls a conventional `utf8_main(int,char**)`.

## Important APIs, types, and functions
It declares `extern int utf8_main(int,char**)` and implements `wmain()`. `WideCharToMultiByte(CP_UTF8,...)` is used first to size and then to populate each UTF-8 argument. Allocated argument strings are freed after `utf8_main()` returns.

## Control flow
`wmain()` allocates an argv array, converts each wide argument, null-terminates the array, calls `utf8_main(argc, argv)`, frees the allocated strings and array, and returns the wrapped program's exit code.

## State and persistence behavior
No persistent state. It only allocates transient process memory.

## Dependencies and integration points
It depends on Win32 APIs and standard C allocation/stdio. Programs include it after redefining `main` to `utf8_main` under `_WIN32`, allowing portable source to receive UTF-8 arguments on Windows.

## Risks and edge cases
If conversion fails for an argument, that argv slot becomes NULL; wrapped programs may not expect NULL inside `argv[0..argc)`. Allocation failures exit immediately. This file is Windows-only because it includes `windows.h`.

## Test signals
Tests should invoke a wrapped tool with ASCII, non-ASCII, and conversion-edge command lines, verifying `utf8_main()` receives UTF-8 bytes and exit codes propagate.
