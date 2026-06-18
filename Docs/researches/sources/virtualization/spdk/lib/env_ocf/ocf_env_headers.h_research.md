# File Research: sources/virtualization/spdk/lib/env_ocf/ocf_env_headers.h

Small OCF environment header shim.

Important behavior:
- Includes `spdk/stdinc.h`.
- Defines OCF version macros: main `20`, major `3`, minor `0`.

Role: gives imported OCF code a stable environment/version header when compiled inside SPDK.
