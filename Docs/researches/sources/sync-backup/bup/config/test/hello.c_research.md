# sources/sync-backup/bup/config/test/hello.c

## Purpose
Minimal configure-time C compiler sanity probe.

## Important APIs, Types, and Functions
Includes `<stdio.h>` and defines `main` that prints `Hello world!`.

## Control Flow
`configure` attempts to compile it with `-Wall -Werror`; execution is not required.

## State and Persistence Behavior
No state. Compile failure aborts configuration before generated config files are written.

## Dependencies and Integration Points
Used by `configure` to validate the selected `CC`.

## Risks and Test Signals
Signals are successful compilation with strict warnings. Risk is minimal; if this fails, the C toolchain is unusable for bup.
