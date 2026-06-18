# File Research: sources/virtualization/nbdkit/filters/ip/rules.h

Declares the opaque `struct rule`, global `late_filtering`, and rule operations used by `ip.c`.

Exports `print_rules()`, `free_rules()`, `parse_rules()`, and `check_if_allowed()`. This header keeps parsing/evaluation details private to `rules.c`.
