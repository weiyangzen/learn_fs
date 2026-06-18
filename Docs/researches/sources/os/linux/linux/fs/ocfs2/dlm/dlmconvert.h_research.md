# File Research: sources/os/linux/linux/fs/ocfs2/dlm/dlmconvert.h

## Purpose
Small interface header for OCFS2 DLM lock conversion.

## Exposed API
- `dlmconvert_master()` converts a lock on a locally mastered resource.
- `dlmconvert_remote()` converts a lock by contacting a remote resource master.

## Notes
The header is guarded by `DLMCONVERT_H` and relies on DLM core types declared elsewhere. It intentionally exposes only the two conversion entry points used by the lock path.
