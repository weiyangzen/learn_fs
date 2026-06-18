# File Research: sources/os/plan9/plan9/sys/src/cmd/eqn/text.c

Text token conversion and spacing logic for `eqn`.

Key behavior:
- Defines class spacing matrix used between mathematical text classes.
- Converts quoted text, spaces, thin spaces, tabs, reserved words, and ordinary tokens into troff strings.
- Handles UTF input via multibyte conversion and classifies letters, digits, punctuation, relations, arrows, spaces, troff escapes, and special italic `f`/`j`.
- Emits font changes, roman overrides, padding, and escaped troff sequences.
- Tracks left/right fonts and classes for later spacing.

Filesystem relevance:
- Text conversion only; no filesystem operations.
