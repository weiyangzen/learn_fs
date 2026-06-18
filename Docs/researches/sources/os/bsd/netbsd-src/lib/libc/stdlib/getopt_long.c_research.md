# File Research: sources/os/bsd/netbsd-src/lib/libc/stdlib/getopt_long.c

Read completely: 479 lines.

Implements `getopt_long()` and, for nbtool replacement builds, `getopt()`. The shared `getopt_internal()` handles short options, optional and required arguments, `optreset`, `optind == 0` compatibility, POSIXLY_CORRECT behavior, GNU-style argument permutation, in-order non-option returns, and `-W` long-option dispatch.

Long-option handling supports `--name`, `--name=value`, abbreviated matches, ambiguity detection, no-argument validation, required and optional arguments, `flag` assignment, and optional index output. Error behavior is controlled by `opterr`, leading `:` in options, and leading `+`/`-` option modifiers.

Important helpers include `gcd()` and `permute_args()`, which rotate non-option and option argument blocks in-place. The implementation uses global getopt state and is therefore stateful across calls.
