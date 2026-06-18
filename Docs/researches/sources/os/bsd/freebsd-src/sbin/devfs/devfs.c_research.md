# File Research: sources/os/bsd/freebsd-src/sbin/devfs/devfs.c

## Purpose
Top-level command dispatcher and utility helpers for controlling devfs mount rules.

## Main Elements
- Opens target mount point from `-m` or defaults to `/dev`.
- Dispatches `rule` and `ruleset` commands.
- Numeric helpers: `atonum()`, `eatoi()`, and `eatonum()`.
- `efgetln()`: malloc-backed line reader that handles newline and non-newline-terminated lines.
- `tokenize()`: splits a rule line into argv-style tokens while preserving one allocated backing string.
- `usage()`: prints command forms.

## Dependencies And Integration
Shares `mpfd` mount-point descriptor with `rule.c`. Includes declarations from `extern.h`.

## Risk Notes
`tokenize()` returns early with allocated `wline` when there are zero tokens, which is acceptable for short-lived command execution but notable.
