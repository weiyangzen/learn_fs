# File Research: sources/os/linux/linux/fs/dlm/ast.h

## Role

Internal declarations for DLM AST/BAST callback handling.

## Exposed Functions

- `dlm_may_skip_callback()`
- `dlm_get_cb()`
- `dlm_add_cb()`
- `dlm_callback_start()`
- `dlm_callback_stop()`
- `dlm_callback_suspend()`
- `dlm_callback_resume()`

## Research Notes

This header exposes callback suppression/allocation and lockspace callback lifecycle controls to the wider DLM implementation.
