# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/tem.h

## Purpose
Defines the kernel-facing terminal emulator public API for virtual terminal state creation, activation, mode changes, output, size queries, framebuffer mode, and STREAMS queue attachment.

## Main Interfaces
- Opaque types:
  - `tem_modechg_cb_arg_t`
  - `tem_modechg_cb_t`
  - `tem_vt_state_t`
- Kernel APIs:
  - `tem_initialized()`
  - `tem_init()`, `tem_destroy()`
  - `tem_info_init()`
  - `tem_write()`
  - `tem_safe_polled_write()`
  - `tem_get_size()`
  - `tem_register_modechg_cb()`
  - `tem_activate()`, `tem_switch()`
  - `tem_get_fbmode()`, `tem_set_fbmode()`
  - `tem_clean()`
  - `tem_init_q()`

## Dependencies And Relationships
Kernel-only includes STREAMS, visual I/O, credentials, and beep support. Private state and rendering callbacks are in `tem_impl.h`.

## Research Notes
The public header intentionally hides terminal parser and framebuffer/text rendering state behind `tem_vt_state_t`.
