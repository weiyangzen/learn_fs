# File Research: sources/os/plan9/plan9/sys/src/cmd/upas/alias/aliasmail.c

- Role: Translates mail aliases from upas library alias files.
- Control flow: Reads system names, reads alias file list from `namefiles` or `fromfiles`, lowercases input names, searches alias DB files including `#include` directives, and emits local fallback or alias expansion.
- Key functions: `getdbfiles`, `translate`, `lookup`, `attobang`, `compare`, `mklower`.
- Integration: Uses `common.h` String/Sinstack helpers and `UPASLIB`.
- Risks/notes: Intentionally lowercases names, warned in file header. `mklower` mutates `argv` strings in place.
