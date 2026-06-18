<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/color.h -->
## sources/test-tools/strace/src/color.h

Purpose: Declares color mode/kind enums, global color state, initialization, and inline emission helper.

Important APIs and types: `enum color_mode_t`, `enum color_kind_t`, extern `color_mode`, `color_seq_table`, `color_is_enabled`, `color_init`, and `tprint_color_seq`.

Control flow: `tprint_color_seq` emits the sequence for a kind only when colors are enabled.

State and persistence: Exposes global process-wide color configuration owned by `color.c`.

Dependencies and integration: Includes `<stdbool.h>` and uses `tprints_string_uncol` from the output layer.

Risks: Callers must pass valid `COLOR_*` enum values below `COLOR_KIND_MAX`. Color output depends on `color_init` being called before printing.

Test signals: Output tests should verify no escape sequences when disabled and correct kind-specific sequences when enabled.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/color.h -->
