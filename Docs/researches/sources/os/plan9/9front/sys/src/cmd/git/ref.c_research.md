# File Research: sources/os/plan9/9front/sys/src/cmd/git/ref.c

Reference expression resolver and commit-graph set algebra. It supports raw hashes, ref names under common prefixes, `HEAD` symbolic refs, hash prefixes, parent suffixes `^`/`~`, LCA operator `@`, and ranges using `:` or `..`.

The central `paint` routine colors commit traversal from heads and tails to compute lowest common ancestors, commits between sets, or ordered ranges. It uses `Objq` and `Objset` to avoid repeated graph work. The file also validates and lists refs recursively under `.git/refs`.
