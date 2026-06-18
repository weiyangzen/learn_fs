# File Research: sources/os/plan9/plan9/sys/src/cmd/mk/mkconv

An `rc` script for converting make-style files toward Plan 9 `mk` syntax.

Behavior:
- Writes input through `tee` to a temp file.
- Runs `sed` rewrites for:
  - Parenthesized make variables to mk/rc-style forms.
  - Leading recipe command markers.
  - Error-handling recipe prefixes.
  - Pattern variables such as `$%`, `$@`, `$^`, `$?`.
  - `:&` to `:`.
- Warns to stderr when recipes contain `cd` or `make`, since those need manual review.
- Cleans temp file on exit or interrupt.

Role:
- Migration helper, not part of the `mk` binary.
