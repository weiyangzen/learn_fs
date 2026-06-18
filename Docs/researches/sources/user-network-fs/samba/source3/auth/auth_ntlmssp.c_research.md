# sources/user-network-fs/samba/source3/auth/auth_ntlmssp.c

## Purpose
This file supplies the source3 implementations of the auth4 hooks used by NTLMSSP and other GENSEC modules: challenge get/set, asynchronous password checking, and session-info generation.

## Important APIs, Types, and Functions
Public functions are `auth3_generate_session_info`, `auth3_get_challenge`, `auth3_set_challenge`, `auth3_check_password_send`, and `auth3_check_password_recv`. The request state type `auth3_check_password_state` stores `authoritative`, `server_info`, and NT/LM session keys.

## Control Flow
`auth3_generate_session_info` handles two input shapes: `auth_user_info_dc` for SCHANNEL/local-system or anonymous tokens, and `auth_serversupplied_info` for normal auth3 password results. `auth3_check_password_send` maps the supplied user info, calls `auth_check_ntlm_password`, maps selected failures to guest server info, sets current user substitution state, reloads shares, extracts NT and LM session keys out of `server_info`, and completes a tevent request. `recv` moves the server info and keys to caller ownership.

## State and Persistence
State lives in the tevent request and the underlying `auth_context` stored in `auth4_context->private_data`. Successful logons alter process-global current user substitution state and trigger `lp_load_with_shares`. Session-key blobs are moved out of server info so the NTLMSSP layer can choose final key handling.

## Dependencies and Integration Points
The file depends on source3 auth dispatch, user mapping, tevent request helpers, local token creation, guest mapping policy, loadparm share reloads, and security token constants for system/anonymous SIDs.

## Risks and Test Signals
Risks include incorrect user remapping propagation, guest mapping on the wrong status, losing session keys through ownership mistakes, and share reload behavior depending on sanitized user names. Tests should cover normal NTLMSSP success, bad-user/bad-password guest mapping, authoritative flag handling, system/anonymous SCHANNEL generation, and key extraction lengths.
