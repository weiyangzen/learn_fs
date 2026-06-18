# File Research: sources/virtualization/spdk/module/bdev/gpt/Makefile

## Purpose
Builds the SPDK GPT bdev module library.

## Main Contents
Declares shared-object version `8.0`, compiles `gpt.c` and `vbdev_gpt.c`, sets `LIBNAME = bdev_gpt`, uses `spdk_blank.map`, and includes SPDK common/lib make fragments.

## Dependencies
Depends only on the SPDK make system and source-local GPT module files.

## Risks and Notes
This file is purely build glue; adding RPC support or additional GPT helpers would require updating `C_SRCS`.
