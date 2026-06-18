# File Research: sources/virtualization/virtiofsd/Cargo.toml

## Scope

Rust package manifest for the virtiofsd crate and binary.

## Package And Features

- Package name `virtiofsd`, version `1.13.3`, Rust edition 2018.
- License is `Apache-2.0 AND BSD-3-Clause`.
- Default feature is `seccomp`.
- `seccomp` exposes optional `libseccomp-sys`.
- `xen` feature switches vhost/vm-memory dependencies to Xen support and explicitly disables normal QEMU/KVM support.
- The `virtiofsd` binary requires `seccomp`.

## Dependencies

Key dependencies include `vhost-user-backend`, `vhost`, `virtio-queue`, `virtio-bindings`, `vm-memory`, `vmm-sys-util`, `capng`, `libc`, `clap`, `serde`, `postcard`, `futures`, `syslog`, and `env_logger`.

## Build Behavior

Release builds enable LTO. `.gitlab-ci.yml` is excluded from the published crate.
