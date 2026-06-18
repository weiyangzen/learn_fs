# File Research: sources/virtualization/virtiofsd/50-virtiofsd.json

## Scope

QEMU/vhost-user backend metadata file describing the virtiofsd executable.

## Contents

- Declares description `virtiofsd vhost-user-fs`.
- Declares backend type `fs`.
- Points QEMU tooling to `/usr/libexec/virtiofsd`.
- Advertises `migrate-precopy` and `separate-options`.

## Role

This file is packaging/runtime integration metadata, not executable logic. It aligns with `main.rs --print-capabilities`, which prints the same capability feature names.
