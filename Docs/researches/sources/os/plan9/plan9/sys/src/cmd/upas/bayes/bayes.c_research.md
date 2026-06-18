# File Research: sources/os/plan9/plan9/sys/src/cmd/upas/bayes/bayes.c

- Role: Classifies message token hash files against multiple mailbox/class hash tables.
- Algorithm: For each message token, computes per-class frequencies normalized by message count, clamps probabilities, retains the most informative words, multiplies class probabilities, and prints best class plus confidence.
- Inputs: `boxhash ... ~ msghash ...`; options enable debug, keyword output, and max informative words.
- Integration: Uses `Hash`/`Stringtab` serialized tables from `hash.c`.
- Risks/notes: Multiplies many doubles directly and can underflow for larger `mbest`; current default is small.
