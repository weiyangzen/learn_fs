# File Research: sources/os/bsd/netbsd-src/lib/libform/type_integer.c

Defines builtin `TYPE_INTEGER`.

Arguments include `precision`, `min`, and `max`. Field validation accepts optional leading sign, digits, and trailing blanks, converts via `atol`, enforces the configured range when `min <= max`, then rewrites buffer 0 with `asprintf("%.*ld", precision, number)`.

Character validation accepts digits, `+`, and `-`.
