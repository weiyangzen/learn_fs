# File Research: sources/virtualization/nvme-cli/libnvme/tools/check-public-headers.py

This Python tool validates that every symbol exported in libnvme version scripts has a declaration/prototype in an installed public header.

Inputs:
- Preferred Meson mode: repeated `--ld FILE` and `--header FILE` arguments.
- Standalone mode: optional source root; auto-discovers `src/*.ld` and `src/nvme/*.h` excluding headers with `private` in the filename.

Algorithm:
- Parses `.ld` files line by line with `^\s+([a-z]\w+);` to collect exported symbol names.
- Parses headers with regex `\b([a-z_]\w+)\s*\(` to collect function-like identifiers.
- Reports any exported symbol missing from all installed headers.
- Exits 1 on errors; otherwise prints an OK count.

Integration:
- `libnvme/test/meson.build` registers it as `libnvme - check-public-headers`.
- Complements `check-public-symbols.py`: this tool checks ABI exports are declared for users.

Risk and maintenance notes:
- Regex parsing is intentionally lightweight. It may count macro invocations or comment text as declarations, though the libnvme/libnvmf namespace reduces practical false positives.
- Symbols not beginning with lowercase letters are ignored by the `.ld` parser.
