# File Research: sources/local-fs/gfs2-utils/gfs2/mkfs/progress.h

Header for the mkfs progress bar helper.

Defines `struct gfs2_progress_bar` with:
- `uint64_t max`
- `int max_digits`
- `int skip_progress`

Exports initialization, update, and close functions.

Research notes:
- The header assumes `uint64_t` is already visible to including files.
