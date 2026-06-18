# File Research: sources/os/bsd/freebsd-src/sbin/kldconfig/kldconfig.c

## Purpose
Implements the `kldconfig` utility for reading and modifying the kernel module search path, normally `kern.module_path`.

## Main Responsibilities
- Reads the module path sysctl.
- Parses semicolon-separated module path components into a tail queue.
- Adds, inserts, removes, deduplicates, prints, and writes path components.
- Supports overriding the sysctl name with `-S`.

## Key Implementation Details
- `getmib()` resolves the sysctl name to a MIB once.
- `getpath()` reads current sysctl value with a two-step size/data sysctl call.
- `setpath()` rebuilds the path string and writes it back with `sysctl()`.
- `addpath()` canonicalizes via `realpath()` when possible, strips trailing slash, rejects duplicates unless forced, and supports insertion before previously inserted paths.
- `rempath()` mirrors path normalization before removal.
- `parsepath()` splits path strings on `;`, optionally enforcing uniqueness.
- `qstring()` reconstructs a semicolon-separated sysctl value.

## Command-Line Behavior
Options include:
- `-d` remove paths.
- `-f` suppress duplicate/missing diagnostics.
- `-i` insert before existing path elements.
- `-m` merge with existing path.
- `-n` dry run.
- `-r` print current path.
- `-S` select sysctl name.
- `-U` remove duplicates.
- `-v` verbose display.

## Notable Edge Cases
- With no arguments, it defaults to merge mode.
- `-r` cannot be combined with path arguments.
- If replacing a non-empty current path without merge/list/unique behavior, `changed` is set even before adding new entries.
