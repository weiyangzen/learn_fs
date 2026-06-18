# File Research: sources/os/plan9/plan9/sys/src/cmd/uniq.c

Read fully: 165 lines, 2185 bytes. SHA-256 prefix: `8c7ba1126a9a7c8b`.

This is Plan 9’s `uniq` implementation for adjacent duplicate lines.

Behavior:
- Options parsed in historical style: `-<number>` skips fields, `+<number>` skips characters after fields, and `-u`, `-d`, `-c`, `-s` set output/comparison modes.
- Reads from stdin or one file using `Biobuf`.
- `gline()` reads newline-delimited records into fixed-size buffers.
- `equal()` compares lines after optional field/letter skipping; mode `s` treats a shorter first line ending at NUL as equal.
- `pline()` prints all, unique-only, duplicate-only, or counted output depending on `mode`.
- `skip()` advances past fields and letters for comparison.

Risk notes: only adjacent duplicates are considered. Lines longer than `SIZE` cause a fatal error; allocated buffers are not resized despite `bsize` being a variable.
