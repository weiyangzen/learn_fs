# sources/security-integrity/selinux/gui/sepolgen

## Purpose
`sepolgen` is a minimal shell wrapper for SELinux policy generation. It forwards all command-line arguments to `sepolicy generate`.

## Important APIs, types, and functions
The file uses `/bin/sh` and a single `exec sepolicy generate "$@"`. `exec` replaces the wrapper process with the `sepolicy` process, preserving signal and exit-status behavior for callers.

## Control flow
When invoked, the shell expands `"$@"` as the original argument vector and transfers control to `sepolicy generate`. There is no validation, branching, or fallback.

## State and persistence behavior
The wrapper has no state. Any generated files or policy side effects are produced by `sepolicy generate`, not this script.

## Dependencies and integration points
It depends on `sepolicy` being available in `PATH` and on the `generate` subcommand. It integrates as a compatibility or convenience command for callers expecting `sepolgen`.

## Risks and edge cases
If `sepolicy` is missing or lacks the `generate` subcommand, launch fails with the shell's command-not-found or command error. The wrapper deliberately performs no privilege handling, environment sanitization, or argument validation.

## Test signals
Tests should verify argument preservation, exit-code propagation, and behavior when `sepolicy` is absent or returns an error. Packaging tests should confirm executable mode and installed path.
