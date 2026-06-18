# File Research: sources/os/bsd/netbsd-src/lib/libedit/tokenizern.c

## Purpose
Narrow-character build wrapper for `tokenizer.c`.

## Main Content
- Includes `config.h`.
- Defines `NARROWCHAR`.
- Includes `tokenizer.c`, causing the macro-generic implementation to instantiate narrow `char` tokenizer symbols.

## Integration
Built alongside the wide tokenizer variant to expose both narrow and wide libedit tokenizer APIs.

## Risks / Notes
This file intentionally depends on inclusion-based compilation; changes in `tokenizer.c` affect both narrow and wide builds.
