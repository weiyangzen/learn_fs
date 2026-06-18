# sources/test-tools/fio/os/windows/posix/include/libgen.h

Purpose: declares the `basename()` compatibility function for Windows.

Important APIs/types: single API `char *basename(char *path)`.

Control flow and state: implemented in `posix.c` by searching for the last slash or backslash and copying into a static `MAX_PATH` buffer.

Dependencies and integration: lets Unix code include `<libgen.h>` and compile on Windows.

Risks: implementation returns static storage, is not thread-safe, and truncates to `MAX_PATH - 1`. Unlike some POSIX implementations, it does not modify the input path.

Test signals: path cases with `/`, `\`, trailing separators, empty strings, and long names.
