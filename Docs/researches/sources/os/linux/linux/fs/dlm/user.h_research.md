# File Research: sources/os/linux/linux/fs/dlm/user.h

## Role

`user.h` declares the DLM user-device API hooks used by lock and module code.

## Interface

It exposes callback purging/addition, user device init/exit, per-lockspace device deregistration, and daemon availability detection.

## Research Notes

Read completely. The implementation is in `user.c`.
