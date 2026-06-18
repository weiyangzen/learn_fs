# sources/sync-backup/bup/lib/bup/cmd/random.py

## Purpose
`random.py` emits deterministic pseudo-random bytes, primarily for tests, benchmarks, and data generation pipelines.

## APIs and Control Flow
`main(argv)` requires exactly one byte-count argument, parses it with `parse_num`, installs Ctrl-C handling, and only writes binary data to stdout when `--force` is set or stdout is not a terminal. Actual generation is delegated to `_helpers.write_random(fd, total, seed, verbose_flag)`.

## State, Dependencies, Integration, Risks, Tests
The command persists nothing but can flood stdout with binary data. Dependencies are compiled helper generation, terminal detection through `istty1`, and parse helpers. Risks include accidental terminal corruption, huge byte counts, and seed semantics depending on `_helpers.write_random`. Test signals include parse suffixes, tty refusal without `-f`, deterministic output for a seed, verbose byte counter behavior, and Ctrl-C handling.
