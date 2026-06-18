# File Research: sources/os/bsd/netbsd-src/lib/libedit/makelist

## Purpose
Shell/AWK generator for libedit's derived command-list headers.

## Modes
- `-h`: generates prototypes for editor functions found by scanning `vi_*`, `em_*`, and `ed_*` comment/function markers.
- `-bh`: generates the `el_func_help[]` binding-help table from function names and nearby comments.
- `-fh`: generates uppercase numeric command constants plus `EL_NUM_FCNS`.
- `-fc`: generates the `el_func[]` dispatch table of function pointers.

## Inputs And Outputs
The script reads source or header files listed on the command line. It emits generated C header content to stdout and does not write files itself.

## Dependencies
Uses `/bin/sh`, `sed`, `awk`, `sort`, and `tr`.

## Risks And Notes
Parsing is intentionally simple and format-sensitive. Function marker/comment formatting in editor command source files must remain compatible, or generated command IDs, help text, and dispatch tables can drift.
