# File Research: sources/os/plan9/9front/sys/src/cmd/mv.c

Plan 9 `mv` implementation.

Behavior:
- Supports `mv fromfile tofile` and `mv fromfile ... todir`.
- Cleans input pathnames before processing.
- Determines destination directory/element based on whether the final argument is an existing directory and whether the source is a directory.
- For same-directory moves, removes an existing target, then attempts `dirwstat` to rename the source.
- If rename cannot work and the source is not a directory, copies file contents to the target, preserves mode and mtime via `dirfwstat`, and removes the source.
- Refuses to copy directories across directories/devices.
- Handles append-only targets by hard-removing before create, since create would not truncate them.
- Uses `samefile` to reject no-op moves by comparing qid/dev/type metadata.
- `hardremove` repeatedly removes a target and exits on first failure.

Important interactions:
- Uses Plan 9 directory metadata, `dirwstat`, `create`, `remove`, `dirstat`, and `IOUNIT`.

Notable quirks:
- Removing an existing target happens before attempting same-directory rename.
- Cross-directory directory moves are refused rather than recursively copied.
