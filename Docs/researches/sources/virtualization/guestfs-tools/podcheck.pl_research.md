# File Research: sources/virtualization/guestfs-tools/podcheck.pl

## Role

Perl test utility that compares a tool’s real command-line options with its POD documentation and `--help` output.

## Behavior

The script accepts `input.pod tool` plus options: `--ignore`, `--insert`, `--verbatim`, and `--path`. It slurps the POD, applies explicit insertions, resolves `__INCLUDE:*.pod__` through optional search paths, applies verbatim insertions, and resolves `__VERBATIM:*.txt__`.

It runs the target tool with `--long-options`, `--short-options`, and `LANG=C --help`. Tool option names become the authoritative set, with a few automatic ignores such as `--color`, `--colour`, and `--debug-gc`.

It then checks that every non-ignored tool option appears as a POD `=item ... B<--option>` entry, checks that POD does not document unknown options except for a few removed subscription-manager options, and checks that help output mentions exactly the known options, ignoring `--options` as a synopsis placeholder.

## Research Notes

This script is the shared enforcement mechanism used by the docs tests in this group. It supports podwrapper-like preprocessing so generated manpage content can still be checked at source-test time.
