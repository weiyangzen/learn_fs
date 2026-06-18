# File Research: sources/os/bsd/freebsd-src/sys/sys/gpt.h

## Purpose
Thin compatibility wrapper that defines GPT UUID type and includes the shared GPT disk layout header.

## Main Interfaces
- Includes `sys/uuid.h`.
- Defines `GPT_UUID_TYPE` as `struct uuid`.
- Includes `sys/disk/gpt.h`.

## Dependencies And Integration
This lets consumers include `sys/gpt.h` and receive GPT structures parameterized with FreeBSD `struct uuid`.

## Risk Notes
The wrapper is intentionally minimal. Any layout semantics live in `sys/disk/gpt.h`; changing `GPT_UUID_TYPE` would affect GPT structure ABI.
