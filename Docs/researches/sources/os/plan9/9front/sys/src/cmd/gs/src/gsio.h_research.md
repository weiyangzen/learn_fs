# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gsio.h

## Role

`gsio.h` prevents Ghostscript library/interpreter code from using standard C `stdin`, `stdout`, `stderr`, and convenience stdio functions directly.

This is IO discipline/build-time guard infrastructure, not filesystem code.

## Main Behavior

The header undefines and redefines `stdin`, `stdout`, `stderr`, `fgetchar`, `fputchar`, `getchar`, `gets`, `printf`, `putchar`, `puts`, `scanf`, `vprintf`, and `vscanf` to invalid identifiers/expressions so accidental direct use causes compile errors.

## Notable Risks

This is intentionally macro-invasive and must be included only where direct stdio use is prohibited. It does not block all possible stdio APIs; comments mention `perror` is not handled because of historical portability issues.
