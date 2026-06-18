# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/iutil.h

Declares the interpreter utility API implemented by `iutil.c`. It covers ref copying, null initialization, object equality and identity, name/string data extraction, printable conversion, array and packed-array access, VM-space checks, string conversion, numeric operand extraction, real/float/int parameter helpers, real construction, and matrix read/write helpers.

It also defines `CVP_MAX_STRING`, the truncation threshold for full string printing, and compatibility macros such as `refset_null`, `write_matrix_new`, and `write_matrix`.
