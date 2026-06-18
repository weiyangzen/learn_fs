# File Research: sources/virtualization/nvme-cli/libnvme/tools/check-public-symbols.py

This Python tool checks consistency between `__libnvme_public` annotations in C sources and exported symbols in libnvme version scripts.

Inputs:
- Optional libnvme source root, defaulting to the parent of the script directory.
- Fixed version scripts: `libnvme.ld`, `libnvmf.ld`, `libnvme-mi.ld`, `accessors.ld`, and `accessors-fabrics.ld`.
- C sources from `src/nvme/*.c`.

Algorithm:
- Collects `.ld` entries using `^\s+([a-z]\w+);`.
- Collects public definitions using a multiline regex matching lines starting with `__libnvme_public` and extracting the last identifier before `(`.
- Reports:
  - public C definitions missing from all version scripts
  - version-script entries without a corresponding `__libnvme_public` definition
- Exits 1 on any mismatch.

Integration:
- Registered by Meson as `libnvme - check-public-symbols`.
- Protects against hidden ABI drift when compile-time visibility and linker version scripts disagree.

Risk and maintenance notes:
- Only scans top-level `src/nvme/*.c`; public definitions outside that glob would be missed.
- Requires `__libnvme_public` to appear at the start of a line.
