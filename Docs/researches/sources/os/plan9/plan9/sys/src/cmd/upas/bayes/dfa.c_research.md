# File Research: sources/os/plan9/plan9/sys/src/cmd/upas/bayes/dfa.c

- Role: Converts Plan 9 regexp NFAs into minimized deterministic regex programs and executes/serializes them.
- Key functions: `dregcvt`, `dregexec`, `Bprintdfa`, `Breaddfa`; helper phases include empty-transition closure, interesting-rune detection, transition exploration, minimization, and compact program construction.
- Data structures: Internal `Deter` state and `Reiset` sets; public `Dreprog`, `Dreinst`, and `Drecase`.
- Integration: Used by `regen.c` to precompile classifier regexes and by `msgtok.c` to tokenize messages.
- Risks/notes: Handles only 16-bit rune space in `findchars`; uses `longjmp` for allocation/format errors.
