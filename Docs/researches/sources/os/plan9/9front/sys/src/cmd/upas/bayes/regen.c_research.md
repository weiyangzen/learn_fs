# File Research: sources/os/plan9/9front/sys/src/cmd/upas/bayes/regen.c

This command generates DFA tables for the Bayesian tokenizer/classifier regexp set.

Key behavior:
- Defines three regexp classes: a `^From ` detector, keyword token regexp(s), and a large ignore-pattern regexp list for HTML/comment/mail-noise/base64/uuencoded/minor tokens.
- `strcpycase` rewrites lowercase ASCII outside character classes into case-insensitive bracket alternatives.
- `dregcomp` compiles regexps with `regcomp`, converts them to DFA programs via `dregcvt`, then frees the original `Reprog`.
- `buildre` builds the three DFA regexps, and `main` prints them with `Bprintdfa`.
- Provides `regerror` as `sysfatal`, making regexp compilation failures fatal.

Integration and risks:
- Includes `regexp.h` and `dfa.h`; it is a generator for data used by the bayes spam filter pipeline.
- Uses a fixed 16 KiB buffer for combined regexp alternations. The current patterns fit, but adding many patterns can overflow unless checked.
