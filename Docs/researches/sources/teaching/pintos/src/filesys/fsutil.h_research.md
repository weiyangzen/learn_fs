# File Research: sources/teaching/pintos/src/filesys/fsutil.h

## Purpose
Public declarations for Pintos file-system utility commands.

## Exposed API
- `fsutil_ls`
- `fsutil_cat`
- `fsutil_rm`
- `fsutil_extract`
- `fsutil_append`

## Research Notes
- All functions accept `char **argv`, matching Pintos command-dispatch conventions.
- The header does not include additional dependencies.
