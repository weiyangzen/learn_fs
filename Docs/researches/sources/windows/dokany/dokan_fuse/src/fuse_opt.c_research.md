# File Research: sources/windows/dokany/dokan_fuse/src/fuse_opt.c

Implements libfuse-style option parsing.

Key behavior:
- Manages allocated `fuse_args` with add, insert, and free helpers.
- Supports comma-separated `-o` option groups.
- Matches option templates with exact, `=`, or space-separated parameter forms.
- Handles template actions:
  - direct integer assignment by struct offset;
  - formatted parameter assignment, including allocated `%s`;
  - callback invocation with special keys;
  - keep/discard semantics.
- Converts two-argument options into single logical option strings for processing.
- Preserves non-options and handles `--` non-option marker.
- Re-inserts collected `-o` options into output args.
- `fuse_opt_match` tests a single option against an option table.

Role:
- Core parser used by both helper parsing and Dokan-specific FUSE option parsing.
