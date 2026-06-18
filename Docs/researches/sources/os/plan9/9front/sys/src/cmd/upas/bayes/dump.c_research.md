# File Research: sources/os/plan9/9front/sys/src/cmd/upas/bayes/dump.c

This is a standalone DFA debugging utility. It compiles a regexp argument with `regcomp()`, converts it with `dregcvt()`, dumps the deterministic transition table, then tests remaining argv strings with `dregexec()`.

The dump shows start-state indexes, transition ranges, target states, final states, and loop states. It is useful for inspecting the classifier regexps used by `msgtok`.
