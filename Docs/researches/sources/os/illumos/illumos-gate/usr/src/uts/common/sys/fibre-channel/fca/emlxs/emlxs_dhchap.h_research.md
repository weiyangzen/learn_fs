# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/fibre-channel/fca/emlxs/emlxs_dhchap.h

## Purpose

`emlxs_dhchap.h` defines Emulex DH-CHAP / FC-SP authentication constants, driver state records, negotiation payload layouts, challenge/reply/success/reject message layouts, and Diffie-Hellman group data structures. Its contents are active only under `DHCHAP_SUPPORT`.

## Main Types

`emlxs_auth_cfg_t` stores authentication configuration for a local/remote entity pair: timeout, mode, bidirectional flag, authentication type priorities, hash priorities, DH group priorities, reauthentication interval, status/time, node pointer, and list links.

`emlxs_auth_key_t` stores local/remote password metadata and bytes for an entity pair, with node pointer and list links.

`emlxs_auth_misc_t` stores challenge values, public/session keys, and responder-side private/public/session key state.

`emlxs_port_dhc_t` stores per-port fabric authentication state, status, and time.

`emlxs_node_dhc_t` stores per-node authentication state-machine state, previous state, discovery reference count, auth config/key copies, response timeouts, transaction IDs, initiator/responder flags, negotiated hash/group/bidirectional values, WWN, misc key/challenge state, reauth timing/status, fabric vendor, expected success, deferred I/O pointers, flags, and parent config/key pointers.

Negotiation payload structures include `AUTH_NEGOT_PARAMS_*`, `AUTH_MSG_HDR`, `AUTH_MSG_NEGOT_*`, and null-DH variants.

Message structures include `DHCHAP_REPLY_HDR`, `DHCHAP_CHALL_NULL`, `DHCHAP_CHALL`, `AUTH_RJT`, and `DHCHAP_SUCCESS_HDR`.

`DH_GROUP` describes a Diffie-Hellman group ID, length, and value.

## Constants

The header defines password types, auth modes, protocol IDs, hash IDs, DH group IDs, ELS AUTH message codes, endian-adjusted FC-SP constants, hash lengths, reject reason/explanation codes, maximum message sizes, parameter tags, fabric and node state-machine values, node events, reauth states, fabric vendor IDs, and per-node flags.

It declares a weak reference to `random_get_pseudo_bytes`.

## Research Notes

This header is security-critical for Fibre Channel authentication. It controls how the driver authenticates fabric/target peers and how authentication state can block or defer I/O. The code supports MD5/SHA1 and NULL/1024/1280/1536/2048 DH groups, with many structures reflecting FC-SP wire layout and endian requirements.
