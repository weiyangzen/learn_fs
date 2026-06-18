# File Research: sources/os/plan9/9front/sys/src/cmd/disk/9660/conform.c

Name-conformance map support for ISO 9660-safe filenames.

Key behavior:
- Maintains a sorted `Conform` map of bad original names to generated conforming names.
- `conform` interns the source name, reuses any existing translation, or assigns `Dnnnnnn`/`Fnnnnnn` depending on directory/file status.
- `addtx` inserts translations by atom pointer order and warns on duplicates.
- `wrconform` writes new `_conform.map` entries sorted by generated name, then restores map ordering by original atom.

Notable dependencies:
- Global `map` from `dump9660.c`.
- `atom`, `emalloc`, `erealloc`, `Cwrite`, and `Cpadblock`.

Research notes:
- Pointer ordering is safe only because names are atomized and retained for process lifetime.
- The older `_conform.map` mechanism is still used for dump/update compatibility even though Joliet covers many long-name cases.
