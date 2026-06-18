# sources/security-integrity/selinux/libsepol/cil/src/cil_lexer.h

## Purpose
`cil_lexer.h` defines the token interface between the Flex lexer and the hand-written CIL parser.

## Important APIs, Types, And Functions
It defines token constants `OPAREN`, `CPAREN`, `SYMBOL`, `QSTRING`, `COMMENT`, `HLL_LINEMARK`, `NEWLINE`, `END_OF_FILE`, and `UNKNOWN`. `struct token` carries token type, token value pointer, and line number. Public functions are `cil_lexer_setup`, `cil_lexer_destroy`, and `cil_lexer_next`.

## Control Flow
The header has no runtime flow. The parser sets up a buffer, repeatedly requests the next token, and destroys scanner state at exit.

## State And Persistence Behavior
Lexer state is maintained in the generated scanner. Token values point into the scanned buffer/global lexer state, so callers must intern or copy values that need longer lifetime.

## Dependencies And Integration Points
`cil_parser.c` is the direct consumer. Unit tests under the CIL test tree exercise setup and token iteration.

## Risks And Edge Cases
The scanner expects a Flex-compatible scan buffer with required trailing NUL bytes. Callers passing the wrong size can cause scanner setup failure or truncated input.

## Test Signals
Lexer tests should cover parentheses, symbols, quoted strings, comments, line markers, newlines, EOF, and unknown characters, including line-number behavior.
