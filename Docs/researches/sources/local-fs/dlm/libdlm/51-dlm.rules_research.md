# File Research: sources/local-fs/dlm/libdlm/51-dlm.rules

## Purpose
udev rules for DLM misc devices.

## Rules
- Creates `/dev/misc/dlm-control` and `/dev/misc/dlm-monitor` with mode `0666`.
- Creates `/dev/misc/dlm_plock` with mode `0666`.
- Creates symlinks for `dlm_*` devices under `/dev/misc/%k` with mode `0660`.

## Notes
- These rules are required by `libdlm.c`, which waits for `/dev/misc/dlm-control` and per-lockspace `/dev/misc/dlm_<lockspace>` paths.
