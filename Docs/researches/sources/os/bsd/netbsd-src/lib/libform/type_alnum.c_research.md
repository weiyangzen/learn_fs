# File Research: sources/os/bsd/netbsd-src/lib/libform/type_alnum.c

Defines builtin `TYPE_ALNUM`.

It stores one argument, `width`, and validates that a field buffer contains a non-empty alphanumeric token, surrounded only by spaces or tabs, whose length does not exceed `width`. On successful field validation it normalizes buffer 0 to the trimmed token.

Character validation accepts `isalnum` characters only. The builtin `FIELDTYPE` has argument lifecycle callbacks and no choice callbacks.
