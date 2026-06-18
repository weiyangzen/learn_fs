# File Research: sources/virtualization/qemu/block/export/vhost-user-blk-server.h

## Purpose
Small public header for the vhost-user block export driver.

## Contents
- Header guard `VHOST_USER_BLK_SERVER_H`.
- Includes `block/export.h`.
- Declares:
  - `extern const BlockExportDriver blk_exp_vhost_user_blk;`

## Role
Allows `block/export/export.c` or equivalent registration code to reference the vhost-user block export driver implemented in `vhost-user-blk-server.c`.
