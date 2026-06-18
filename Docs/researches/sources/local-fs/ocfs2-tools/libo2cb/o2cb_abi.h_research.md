# File Research: sources/local-fs/ocfs2-tools/libo2cb/o2cb_abi.h

## Purpose

Defines configfs path format strings and heartbeat flag constants used by `o2cb_abi.c`.

## Main Contents

- Notes that modern configfs is under `/sys/kernel/config`, while older O2CB used `/config`.
- Format macros for cluster directory, cluster path, node directory, node path, node attributes, heartbeat directory, heartbeat region, heartbeat region attributes, and heartbeat mode.
- Defines `OCFS2_CLUSTER_O2CB_GLOBAL_HEARTBEAT` flag.

## Dependencies and Integration

- Private implementation header for libo2cb ABI code.
- Path macros take the detected configfs prefix plus cluster/node/region names.

## Research Notes

- This header duplicates the global heartbeat flag also present in `ocfs2_fs.h`; the value must stay aligned.
