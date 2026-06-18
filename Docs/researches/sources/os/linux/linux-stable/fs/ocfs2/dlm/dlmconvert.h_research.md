# File Research: sources/os/linux/linux-stable/fs/ocfs2/dlm/dlmconvert.h

## Purpose

`dlmconvert.h` declares the two conversion entry points used by the lock path.

## API

- `dlmconvert_master(struct dlm_ctxt *dlm, struct dlm_lock_resource *res, struct dlm_lock *lock, int flags, int type)`
- `dlmconvert_remote(struct dlm_ctxt *dlm, struct dlm_lock_resource *res, struct dlm_lock *lock, int flags, int type)`

The caller chooses the function based on whether `res->owner == dlm->node_num`.

## Role In The DLM

This header is consumed by `dlmlock.c`, where `dlmlock()` routes `LKM_CONVERT` requests to the local or remote conversion path. It keeps conversion internals separated from general lock creation.
