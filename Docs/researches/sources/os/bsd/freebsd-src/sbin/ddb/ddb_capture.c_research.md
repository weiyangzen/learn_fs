# File Research: sources/os/bsd/freebsd-src/sbin/ddb/ddb_capture.c

## Purpose
Prints and reports status for the DDB capture buffer from either a live kernel or a crash dump.

## Main Elements
- Sysctl names for live capture data, buffer offsets, size, max size, and in-progress state.
- `namelist[]`: kernel symbols for libkvm crash-dump reads.
- `kread()` / `kread_symbol()`: wrappers for exact-size `kvm_read()`.
- `ddb_capture_print_kvm()` / `ddb_capture_status_kvm()`: read capture data and metadata from crash dumps.
- `ddb_capture_print_sysctl()` / `ddb_capture_status_sysctl()`: read live kernel state through sysctl, retrying data reads on `ENOMEM`.
- `ddb_capture()`: parses `-M` and `-N`, opens kvm if needed, then dispatches `print` or `status`.

## Dependencies And Integration
Uses `libkvm` for crash dumps and `debug.ddb.capture.*` sysctls for live kernels.

## Risk Notes
Crash-dump access depends on exact kernel symbol names. Live buffer reads handle concurrent size changes by retrying when sysctl reports `ENOMEM`.
