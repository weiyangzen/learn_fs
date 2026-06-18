# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gserver.c

## Role

`gserver.c` is a simple procedural server front end for the Ghostscript interpreter, replacing `gs.c` for embedding-style use.

## Public API

Defines:

- `gs_server_initialize`
- `gs_server_run_string`
- `gs_server_run_files`
- `gs_server_terminate`

The API initializes Ghostscript with caller-provided file descriptors, runs strings/files, returns exit/error codes, and can report the PostScript error object as a printable string.

## Initialization

`gs_server_initialize` converts file descriptors to C `FILE *`, calls `gs_init0`, `gs_init1`, and `gs_init2`, then runs `/QUIET true def /NOPAUSE true def` and optional caller initialization code.

## Job State

Non-permanent file runs are wrapped in `job_begin`/`job_end`. `job_begin` erases the current page, saves interpreter state via `zsave`, and stores the save object. `job_end` resets the interpreter, restores the saved object with `zrestore`, and returns to the baseline state.

## Error Reporting

`errstr_report` uses `obj_cvs` to convert the error object into caller storage, falling back to `[unprintable]`.

## Dependencies

Uses interpreter internals (`main.h`, `interp.h`, operand stack, refs, save/restore operators) and graphics erasepage.

## Risks

This is tightly coupled to interpreter globals such as `osp` and `igs`. File descriptor conversion failures leak earlier `FILE *` objects in some paths. The server API is simple but not designed for concurrent interpreter instances.
