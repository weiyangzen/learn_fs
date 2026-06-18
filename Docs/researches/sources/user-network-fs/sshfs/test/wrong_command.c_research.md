# sources/user-network-fs/sshfs/test/wrong_command.c

## Purpose

`wrong_command.c` builds a small executable that intentionally fails with a clear diagnostic telling the user not to run it directly. In the SSHFS Meson test setup, `test/meson.build` builds this program as `wrong_command` from `wrong_command.c`; it acts as a guard or placeholder command that redirects humans toward the real pytest invocation.

## Important APIs, Types, And Functions

- Includes only `<stdio.h>`.
- `int main(void)` writes a colored/bold message to `stderr` with `fprintf`.
- The diagnostic says: "This is not the command you are looking for." and "You probably want to run 'python3 -m pytest test/' instead".
- Returns `1` unconditionally.

## Control Flow

Execution enters `main`, emits ANSI escape sequences for red and bold text, prints the two-line warning, resets terminal styling, and exits with failure status. There are no branches, inputs, allocation, or file operations beyond writing to standard error.

## State And Persistence Behavior

The program has no persistent state. It does not read or write files, environment variables, or process-global state beyond terminal output. Its only externally visible effects are stderr text and exit code `1`.

## Dependencies And Integration Points

- Requires a C compiler and standard C library.
- Integrated by `sources/user-network-fs/sshfs/test/meson.build`, which builds the executable from this source.
- The message points users to `python3 -m pytest test/`, matching the test command used by `travis-build.sh`.

## Risks And Edge Cases

- The source uses both `\x1B` and `\e` escape forms. `\e` is a common compiler extension but is not part of strict ISO C, so strict portability depends on compiler mode.
- ANSI coloring can render literally on terminals or logs that do not interpret escape codes.
- The utility is intentionally always failing; accidentally wiring it into an automated test as the command under test would produce a guaranteed failure.

## Test Signals

- Building this file verifies the test build can compile small C helpers.
- Running the executable should produce the guidance message on stderr and exit with status `1`.
- The absence of dependencies or side effects makes it a stable smoke-test artifact for command-dispatch mistakes.
