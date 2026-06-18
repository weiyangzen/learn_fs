# File Research: sources/os/linux/linux-stable/fs/ocfs2/dlm/dlmdomain.h

## Purpose

`dlmdomain.h` exposes minimal domain state helpers and the domain eviction callback trigger.

## API

Exports:

- `dlm_domain_lock`
- `dlm_domains`
- `dlm_fire_domain_eviction_callbacks(struct dlm_ctxt *dlm, int node_num)`

Inline helpers:

- `dlm_joined()` returns true when `dlm->dlm_state == DLM_CTXT_JOINED`.
- `dlm_shutting_down()` returns true when `dlm->dlm_state == DLM_CTXT_IN_SHUTDOWN`.

Both helpers acquire `dlm_domain_lock` before reading domain state.

## Role In The DLM

This header gives other DLM source files a safe, shared view of high-level domain lifecycle state without exposing the larger registration and join implementation.
