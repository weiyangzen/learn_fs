# File Research: sources/teaching/minix/minix/fs/Makefile

## Purpose

Top-level Makefile for MINIX filesystem services.

## Build Role

Includes `bsd.own.mk`, always builds `mfs` and `pfs`, and when `MKIMAGEONLY` is not `no`, also builds `ext2`, `isofs`, `procfs`, and `ptyfs`. On i386 it additionally builds `hgfs` and `vbfs`. It includes `bsd.subdir.mk` for recursive subdirectory builds.

## Dependencies

Depends on NetBSD bsd make infrastructure and build variables such as `MKIMAGEONLY` and `MACHINE_ARCH`.

## Risks

The conditional appears inverted relative to the variable name: extra filesystems are included when `MKIMAGEONLY != "no"`. That may be intentional for this tree, but it is worth checking before changing build policy.
