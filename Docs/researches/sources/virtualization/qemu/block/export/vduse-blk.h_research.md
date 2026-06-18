# File Research: sources/virtualization/qemu/block/export/vduse-blk.h

## Purpose
Small public header for the VDUSE block export driver.

## Contents
- Header guard `VDUSE_BLK_H`.
- Includes `block/export.h`.
- Declares:
  - `extern const BlockExportDriver blk_exp_vduse_blk;`

## Role
Allows the block export registration layer to reference the `vduse-blk` export driver implemented in `vduse-blk.c`.
