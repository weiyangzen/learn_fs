# File Research: sources/os/plan9/plan9/sys/src/cmd/tbl/tf.c

Saves and restores troff fill, diversion, line-number, and field-control state around table output.

Key functions:
- `savefill` defines macro `SF` to restore point size, vertical spacing, indent, fill, and adjustment, then switches to no-fill.
- `rstofill` invokes the saved macro.
- `endoff` clears line-stop registers, removes text diversions, and emits trailing `last` input.
- `ifdivert` defines string `#d` differently depending on diversion context.
- `saveline` and `restline` preserve troff line counters across table preprocessing.
- `cleanfc` clears field control.

This module is mostly troff state hygiene required before and after generated table requests.
