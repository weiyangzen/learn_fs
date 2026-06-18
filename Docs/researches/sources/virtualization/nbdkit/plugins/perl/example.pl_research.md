# File Research: sources/virtualization/nbdkit/plugins/perl/example.pl

## Purpose
Provides a simple example Perl plugin implementing a persistent in-memory 1 MiB read/write disk.

## Main Entry Points
- `config()` prints and ignores extra parameters.
- `open()` returns a per-client hashref with readonly state.
- `get_size()` returns the size of the global `$disk` string.
- `pread()` returns a substring.
- `pwrite()` replaces a substring with written data.
- `zero()` zeroes when `FLAG_MAY_TRIM` is set, otherwise sets EOPNOTSUPP to request fallback.

## Dependencies
Uses Perl `POSIX` for errno constants and the adapter-provided `Nbdkit` module constants/functions.

## Risks and Notes
The disk is global to the plugin instance, not per connection. The example does not enforce readonly mode in `pwrite()` and is intended as demonstration code.
