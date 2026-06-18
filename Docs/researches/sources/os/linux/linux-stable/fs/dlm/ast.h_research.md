# File Research: sources/os/linux/linux-stable/fs/dlm/ast.h

## Purpose

Declares the DLM callback management interface implemented by `ast.c`.

## Main Responsibilities

- Declares callback suppression and allocation helpers:
  - `dlm_may_skip_callback()`
  - `dlm_get_cb()`
  - `dlm_add_cb()`
- Declares callback lifecycle helpers:
  - `dlm_callback_start()`
  - `dlm_callback_stop()`
  - `dlm_callback_suspend()`
  - `dlm_callback_resume()`

## Dependencies

- Uses DLM lock block and callback types from internal DLM headers.
- Shared by DLM lock/recovery paths that need to enqueue or control callback delivery.
