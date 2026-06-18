# File Research: sources/os/plan9/9front/sys/src/cmd/upas/bayes/bayes.c

This program classifies message token hash files against one or more class hash tables. Invocation separates class hashes and message hashes with `~`.

For each message hash, it computes per-token conditional probabilities from class counts normalized by each class’s `*nmsg*`, keeps the most discriminating tokens, multiplies their probabilities per class, normalizes, and outputs the best class and confidence. `-k` appends keyword evidence, `-D` dumps debug evidence, and `-m` controls how many best words are retained.

It uses the custom `Hash`/`Stringtab` serialization from `hash.c`. Low-frequency tokens are biased toward table 0 with fixed fallback probabilities.
