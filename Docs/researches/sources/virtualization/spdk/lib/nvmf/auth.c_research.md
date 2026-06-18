# File Research: sources/virtualization/spdk/lib/nvmf/auth.c

## Purpose
Implements target-side NVMe-oF DH-HMAC-CHAP authentication for qpairs.

## Main Responsibilities
- Maintains per-qpair authentication state in `struct spdk_nvmf_qpair_auth`.
- Handles authentication send messages: negotiate, DHCHAP reply, DHCHAP success2, and failure2.
- Handles authentication receive messages: challenge, success1, and failure1.
- Negotiates the strongest mutually supported digest and DH group from target policy and host descriptors.
- Generates challenges, sequence numbers, optional DH keys, and derives shared secrets.
- Validates host challenge responses and optionally authenticates the controller back to the host.
- Enforces authentication timeout behavior with SPDK pollers.
- Exposes qpair auth init/destroy/dump and reports support via `nvmf_auth_is_supported()`.

## State Machine
- Starts in `NEGOTIATE`.
- Moves to `CHALLENGE` after successful algorithm selection.
- Sends challenge and moves to `REPLY`.
- Validates host reply and moves to `SUCCESS1`.
- If the host did not request controller authentication, success1 completes and the qpair becomes enabled.
- If controller authentication is requested, moves to `SUCCESS2` and waits for host success2 or failure2.
- Failure paths move through `FAILURE1` or `ERROR`; completed authentication moves to `COMPLETED`.

## Key Interfaces
- Called from controller fabric command routing via `nvmf_auth_request_exec()`.
- Uses `nvmf_subsystem_get_dhchap_key()` for host/controller DHCHAP secrets.
- Uses NVMe DHCHAP helpers for digest length, names, DH key generation, shared secret derivation, and HMAC calculation.
- Uses OpenSSL `RAND_bytes()` for initial subsystem sequence number and challenge values.

## Important Details
- Timeout defaults to 120 seconds if KATO is zero, otherwise follows controller keep-alive timer.
- Reauthentication timeout on an already enabled qpair is nonfatal and returns to `COMPLETED`.
- Negotiation preference arrays are ordered strongest to weakest: SHA512, SHA384, SHA256 and DH groups 8192 down to NULL.
- Failure1 is returned as a successful NVMe command completion carrying an authentication failure payload, then the qpair is disconnected after a short delay.
- JSON dump includes auth state, digest, and DH group.

## Storage Relevance
This file protects NVMe-oF controller sessions before namespace access, making it part of the storage target’s access-control boundary.

## Risks / Notes
- Correctness depends on target-level `dhchap_digests` and `dhchap_dhgroups` bitmasks.
- It carefully validates payload lengths, transaction IDs, hash lengths, DH value alignment, and controller challenge flags before cryptographic checks.
- Controller-authentication support requires a controller DHCHAP key; if absent while requested, authentication fails.
