# File Research: sources/virtualization/libguestfs/daemon/daemon_config.ml.in

Configure-time OCaml template for daemon configuration.

Key points:
- Defines `hivex_flag_unsafe` from `@HIVEX_OPEN_UNSAFE_FLAG@`.
- Used by the OCaml daemon/inspection code after configure substitution.
- No runtime logic beyond exposing the configured constant.
