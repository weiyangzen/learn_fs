# sources/security-integrity/audit-userspace/src/auditd-listen.h

## Purpose
`auditd-listen.h` exposes the listener lifecycle and state-reporting API while compiling to no-op inline functions when listener support is disabled.

## Important APIs, Types, And Functions
When `USE_LISTENER` is defined, it declares `auditd_tcp_listen_init`, `auditd_tcp_listen_uninit`, `auditd_tcp_listen_reconfigure`, and `write_connection_state`. Otherwise it supplies inline stubs for init/uninit/reconfigure, allowing callers to avoid compile-time conditionals.

## Control Flow
Daemon startup calls init after libev setup; shutdown calls uninit; live reconfigure calls reconfigure; state dump calls `write_connection_state` only under listener-enabled builds. The stubbed disabled path returns success and performs no work.

## State And Persistence
The header owns no state. It abstracts whether listener state exists in `auditd-listen.c`.

## Dependencies And Integration
It includes `config.h`, `ev.h`, and `<stdio.h>`, and is used by `auditd.c` and `auditd-reconfigure.c`. The API consumes `struct daemon_conf`, provided by transitive includes in normal builds.

## Risks
The disabled inline `auditd_tcp_listen_reconfigure` signature lacks `const` symmetry with the enabled declaration, which can produce warnings or hide const-correctness issues. Consumers must remember `write_connection_state` only exists in listener builds.

## Test Signals
Build matrix tests with listener enabled and disabled are the main signal. Reconfigure compile coverage is important because this header intentionally changes behavior by preprocessor path.
