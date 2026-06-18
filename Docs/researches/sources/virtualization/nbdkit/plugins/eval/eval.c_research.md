# File Research: sources/virtualization/nbdkit/plugins/eval/eval.c

Implements `nbdkit eval`, a plugin that accepts nbdkit callback bodies as command-line script snippets.

Key behavior:
- Maintains a sorted vector of method name to generated temporary executable script.
- Creates a default `missing` script that exits with code 2, matching shell plugin missing-method semantics.
- Recognizes known nbdkit method keys such as `get_size`, `pread`, `pwrite`, `can_write`, `extents`, `cache`, etc.
- Unknown config keys are passed to the configured `config` callback, if any.
- Requires `get_size` by config completion.
- Synthesizes `can_*` wrappers when a method exists but its capability callback is missing, mirroring C plugin defaults.
- Delegates actual callback execution to shared shell plugin functions via `struct subplugin`.

Lifecycle:
- `eval_load` creates tmpdir and missing script.
- `eval_unload` runs `unload` script if present, tears down tmpdir, frees method scripts, and frees `missing`.
- Registered nbdkit plugin callbacks mostly point to `sh_*` functions from the shell plugin backend.

Security/validation:
- Rejects method names containing `.` or `/`.
- Stores snippets as executable files with mode `0500`.
