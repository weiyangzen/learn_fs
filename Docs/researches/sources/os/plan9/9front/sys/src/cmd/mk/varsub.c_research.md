# File Research: sources/os/plan9/9front/sys/src/cmd/mk/varsub.c

Implements mk variable substitution, including `${name: A%B=C%D}` pattern substitutions.

Key behavior:
- `varsub()` handles `$name`, `${name}`, and substitution forms.
- `varname()` extracts variable names with mk word-character rules.
- `expandvar()` parses braced variables and locates substitution expressions.
- `subsub()` applies prefix/suffix match-and-rewrite across each word of a variable value.
- `submatch()` tests optional prefix/suffix word lists and returns the middle span for `%` substitutions.

Important dependencies: `mk.h`, `getvar`, `stow`, `charin`, `Word` helpers.

Notable risks:
- Substitution syntax is compact and delimiter-sensitive.
- Word-list ownership and temporary buffer reuse are subtle inside `subsub()`.
