# File Research: sources/os/bsd/freebsd-src/sbin/ipf/libipf/buildopts.c

This shared helper parses a comma-separated IPv4 option list and writes encoded options into a caller-provided buffer.

`buildopts()` splits option tokens, separates optional `name=value` class data, finds the option in `ionames`, prevents duplicate option bit classes, appends bytes through `addipopt()`, and pads the final buffer with NOPs followed by EOL to align option length.

Implementation notes:
- Input string is mutated through `strtok()` and `=`.
- Unknown option names print an error and return `0`.
- Padding behavior differs slightly from the `ipsend/ipsopt.c` variant.
