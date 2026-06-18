# File Research: sources/os/plan9/9front/sys/src/cmd/vnc/errstr.h

## Role

`errstr.h` defines the Plan 9-style error strings declared by `error.h`.

## Contents

The file initializes global `char[]` variables for common kernel/device errors such as nonexistence, permission denied, bad argument, I/O error, hung-up channel, no memory, interrupted operation, bad stat buffer, and related conditions.

## Relationship To Code

- Included by `compat.c` to provide exactly one definition site for the error globals.
- Other files include `error.h` to reference them.

## Notable Limitations And Risk Areas

- Because this header contains definitions rather than declarations, it must only be included in one translation unit.
- Error identity is textual; changing these strings can affect user-visible 9P errors and any string comparisons.
