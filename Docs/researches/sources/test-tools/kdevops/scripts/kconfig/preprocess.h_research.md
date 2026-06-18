# sources/test-tools/kdevops/scripts/kconfig/preprocess.h

## Purpose
`preprocess.h` declares the public Kconfig preprocessor interface used by the parser and lexer.

## Important APIs, Types, And Functions
It defines `enum variable_flavor` with `VAR_SIMPLE`, `VAR_RECURSIVE`, and `VAR_APPEND`, forward-declares `struct gstr`, and prototypes `env_write_dep()`, `variable_add()`, `variable_all_del()`, `expand_dollar()`, and `expand_one_token()`.

## Control Flow
The header has no control flow. It establishes that callers can add variables during parse, expand `$()` references while scanning, write environment dependencies after parsing, and release variables after parse completion.

## State And Persistence
State is owned by `preprocess.c`; this header exposes mutation functions without exposing the underlying lists.

## Dependencies And Integration Points
Included by `parser.y` and likely the generated lexer. It depends only on the enum and `struct gstr` forward declaration.

## Risks And Edge Cases
Callers must free strings returned from expansion functions. Flavor semantics must match parser assignment tokens exactly or Kconfig variable behavior changes.

## Test Signals
Compile parser/lexer/preprocess together and exercise assignment plus expansion cases from Kconfig syntax.
