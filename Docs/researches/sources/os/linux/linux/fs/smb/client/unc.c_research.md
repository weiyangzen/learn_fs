# File Research: sources/os/linux/linux/fs/smb/client/unc.c

## Scope
Read completely: 69 lines. This small file provides helper parsing for UNC strings.

## Purpose
`unc.c` extracts the server hostname and share name from CIFS/SMB UNC paths. The helpers allocate newly owned strings for callers.

## Main Interfaces
- `extract_hostname(const char *unc)`
- `extract_sharename(const char *unc)`

## Behavior
`extract_hostname()`:
- Rejects UNC strings shorter than three bytes.
- Skips leading backslashes.
- Requires a backslash delimiter between hostname and share.
- Allocates and returns a NUL-terminated copy of the hostname.
- Returns `ERR_PTR(-EINVAL)` for malformed input and `ERR_PTR(-ENOMEM)` for allocation failure.

`extract_sharename()`:
- Assumes the UNC starts with two leading separator characters and starts parsing at `unc + 2`.
- Finds the next backslash separator.
- Duplicates everything after that separator as the share string.
- Returns `ERR_PTR(-EINVAL)` or `ERR_PTR(-ENOMEM)` on failure.

## Integration Points
These helpers are used by CIFS mount/session setup and UNC normalization paths that need separate server/share fields from a canonical `\\server\share...` style string.

## Notable Behaviors
- Both helpers assume backslash separators.
- `extract_hostname()` tolerates more than two leading backslashes by skipping all initial `\\` characters.
- `extract_sharename()` is stricter in practice because it starts at `unc + 2`; callers must pass a valid canonical UNC string.
- Returned strings must be freed by the caller.

## Risks And Review Focus
- Input validity assumptions differ between hostname and sharename extraction.
- `extract_sharename()` does not explicitly check minimum length before `unc + 2`; it depends on callers providing valid UNC input.
- These helpers do not trim a path after the share; if the input contains `\\server\share\path`, `extract_sharename()` duplicates `share\path`, not just `share`.

## Research Takeaways
`unc.c` is a narrow allocation/parsing utility. Its correctness depends mostly on callers passing normalized UNC strings and knowing whether they need only a share component or a share-plus-path suffix.
