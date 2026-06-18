# File Research: sources/os/plan9/plan9/sys/src/cmd/mk/varsub.c

Implements mk variable substitution and pattern substitution.

Supported forms:
- `$name`
- `${name}`
- `${name: A%B=C%D}` style substitutions using `%` or `&`.

Key functions:
- `varsub()` dispatches braced or simple variable expansion.
- `varname()` parses variable names.
- `varmatch()` looks up non-empty variable values.
- `expandvar()` handles `${name}` and substitution forms.
- `extractpat()`, `subsub()`, and `submatch()` apply prefix/suffix pattern substitutions across word lists.

Behavior notes:
- Missing variables in substitution form produce the variable name as a word.
- Pattern substitution preserves unmatched words.
- Uses `charin()` so parsing respects rc quoting and `${...}` nesting.
