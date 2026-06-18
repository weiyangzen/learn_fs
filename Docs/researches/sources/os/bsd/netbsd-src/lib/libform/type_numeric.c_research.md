# File Research: sources/os/bsd/netbsd-src/lib/libform/type_numeric.c

Defines builtin `TYPE_NUMERIC`.

Arguments include `precision`, `min`, and `max`. Field validation accepts signed decimal/scientific notation, optional fractional part, optional exponent, and trailing blanks. It converts with `atof`, range-checks when `min < max`, and normalizes buffer 0 using fixed decimal formatting with the configured precision.

Character validation accepts digits, signs, `.`, `e`, and `E`.
