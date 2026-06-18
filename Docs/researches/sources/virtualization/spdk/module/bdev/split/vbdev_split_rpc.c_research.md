# File Research: sources/virtualization/spdk/module/bdev/split/vbdev_split_rpc.c

## Purpose
JSON-RPC front-end for split bdev creation and deletion.

## RPCs
- `bdev_split_create`: decodes `base_bdev`, `split_count`, optional `split_size_mb`, calls `create_vbdev_split()`, and returns an array of created split bdev names if the base is present.
- `bdev_split_delete`: decodes `base_bdev`, calls `vbdev_split_destruct()`, and returns boolean success.

## Notable Behavior
After creation, it opens the base bdev and walks the part-base tailq to return the actual split bdev names. If the base is not available yet, creation may succeed as pending config but the returned array will be empty.

## Dependencies
Uses SPDK JSON-RPC, generated RPC cleanup contexts, `spdk_bdev_open_ext()`, and split module helpers.
