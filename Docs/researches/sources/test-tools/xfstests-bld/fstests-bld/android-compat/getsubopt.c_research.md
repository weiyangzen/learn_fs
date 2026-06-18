# sources/test-tools/xfstests-bld/fstests-bld/android-compat/getsubopt.c

Purpose: supplies a BSD-derived implementation of `getsubopt` for Android/bionic environments.

Important APIs and functions: global `char *suboptarg` and exported `getsubopt(char **optionp, char * const *tokens, char **valuep)`.

Control flow: skips leading delimiters, isolates the next token and optional `=value`, updates `*optionp` to the remaining string, compares the token against `tokens`, and returns the matched index or `-1`.

State and persistence: mutates the input option string in place by writing NUL terminators; stores unmatched token start in global `suboptarg`.

Dependencies and integration: used by tools that parse comma-separated mount or command suboptions and expect glibc-like `getsubopt`.

Risks: destructive parsing requires writable input. The global `suboptarg` is not thread-safe. Behavior with quoted delimiters is not supported.

Test signals: callers should observe correct token indexes, `valuep` values, and progressive advancement of `optionp`.
