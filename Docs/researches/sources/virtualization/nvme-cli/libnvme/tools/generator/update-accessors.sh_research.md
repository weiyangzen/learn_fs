# File Research: sources/virtualization/nvme-cli/libnvme/tools/generator/update-accessors.sh

This shell wrapper runs `generate-accessors.py` and either updates generated source files or checks them for drift.

Inputs:
- Required positional args:
  - Python interpreter
  - generator script
  - output `.h`
  - output `.c`
  - output `.ld`
  - one or more input headers
- Optional:
  - `--check`
  - `--swig-out FILE`
  - `--dict-table-out FILE`

Workflow:
- Creates a temporary work directory and removes it on exit.
- Runs the Python generator into temporary `.h`, `.c`, `.ld`, optional `.i`, and optional dict-table files.
- In update mode:
  - `update_if_changed()` atomically replaces `.h`, `.c`, `.i`, and dict-table outputs only when content differs.
  - Does not update `.ld` automatically.
  - Calls `check_ld_drift()` and prints symbols to add/remove as maintainer guidance.
- In check mode:
  - `check_if_current()` compares generated temp files with committed outputs.
  - `check_ld_drift()` compares generated vs committed symbol lists.
  - Exits nonzero if any output is stale or `.ld` symbol list drift is detected.

Important helpers:
- `extract_syms()` extracts linker symbols with `grep`, `sed`, and `sort`.
- `check_ld_drift()` uses `comm` to report added/removed symbols.

Integration:
- Invoked by Meson run targets in `tools/generator/meson.build`.
- Supports CI via `-Dcheck-accessors=true`.

Risk and maintenance notes:
- `.ld` drift is intentionally manual because version-section labels require maintainer decisions.
- The script assumes common Unix tools including `realpath`, `grep`, `sed`, `sort`, and `comm`.
