# sources/user-network-fs/samba/source3/winbindd/winbindd_ccache_access.c

## Purpose

`winbindd_ccache_access.c` handles local winbind requests that save user passwords into the in-memory credential cache and later use those stored credentials to produce NTLMSSP authenticate messages. It is the access-control layer over `WINBINDD_MEMORY_CREDS`.

## Important APIs, Types, and Functions

- `winbindd_ccache_save()` canonicalizes a requested account, verifies the peer UID, and calls `winbindd_add_memory_creds()`.
- `winbindd_ccache_ntlm_auth()` validates the request, locates stored memory credentials, and returns an NTLMSSP auth blob/session key.
- `check_client_uid()` uses `getpeereid()` to verify the request UID.
- `client_can_access_ccache_entry()` permits only the owner UID or UID 0.
- `do_ntlm_auth_with_stored_pw()` drives Samba GENSEC `ntlmssp_resume_ccache`.

## Control Flow

Save requests null-terminate fixed buffers, canonicalize the user, confirm the domain exists, verify socket peer UID, then store the password. NTLM auth requests canonicalize and reparse the user, check the domain and UID, validate negotiate/challenge blob lengths against `extra_len` with overflow checks, find the memory credential record, enforce owner access, and either answer an availability probe or run the GENSEC NTLMSSP state machine. Successful auth copies the generated blob into response extra data and fills a 16-byte session key.

## State and Persistence Behavior

No persistent state is owned here. The file reads and writes process-local memory credentials managed by `winbindd_cred_cache.c`; those may include mlocked password buffers depending on platform support.

## Dependencies and Integration Points

It depends on winbind request structures, username canonicalization/parsing, `find_auth_domain()`, memory credential APIs, and Samba auth-generic/GENSEC NTLMSSP client code. It serves PAM/ntlm_auth-style clients that save credentials and later need challenge responses.

## Risks and Edge Cases

Plaintext passwords are used for response generation. Security depends on correct peer UID checks and memory cache handling. Blob-length validation is critical because data comes from request extra data. Empty blobs are a probe path and must not disclose auth output. Boolean handler returns can hide detailed NT status except in logs/response fields.

## Test Signals

Test UID mismatch denial, UID 0 override, missing credentials, malformed/wrapping blob lengths, zero-length probe success, successful NTLMSSP response generation, session-key length validation, canonical name rewriting, and unknown-domain save failure.
