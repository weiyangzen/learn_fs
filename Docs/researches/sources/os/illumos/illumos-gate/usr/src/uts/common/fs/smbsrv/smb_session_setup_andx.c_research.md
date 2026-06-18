# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/smbsrv/smb_session_setup_andx.c

## Purpose

`smb_session_setup_andx.c` implements SMB1 `SessionSetupAndX` request parsing and response encoding. It supports pre-NTLM 0.12, NTLM 0.12 without extended security, and NTLM 0.12 extended-security session setup flows.

## Main Interfaces

- `smb_pre_session_setup_andx()` decodes the request into `smb_arg_sessionsetup_t`.
- `smb_post_session_setup_andx()` ends tracing and zeroes decoded password buffers.
- `smb_com_session_setup_andx()` updates session limits/capabilities, invokes authentication, maps authentication statuses to SMB errors, and encodes the setup response.

## Behavior And Data Flow

Preprocessing allocates `smb_arg_sessionsetup_t` from request storage and enforces a minimum word count of 10. It decodes the common AndX command/offset, max buffer size, and max multiplex count. For dialects before NT LM 0.12, it decodes only an LM password and optional user/domain strings. For NT LM 0.12 word count 13, it decodes LM and NT password lengths, capabilities, clears extended-security capability defensively, then decodes LM password, NT password, user, and domain. For word count 12, it requires `CAP_EXTENDED_SECURITY`, decodes an input security blob, and defers user/domain identity to extended authentication.

The parser then decodes native OS and native LanMan strings. Native OS/LanMan parsing is tolerant; failures default to NT-style values. NT4 padding quirks are handled by using a different decode pattern when native OS is recognized as Windows NT.

The command path updates session message size, max mpx, capabilities, and native OS/LM on first calls. If server configuration requires encryption, SMB1 access is rejected. Authentication is delegated to `smb_authenticate_ext()` for extended security or `smb_authenticate_old()` for legacy forms. Success and continuation responses include guest action flag, optional output security blob, and server native OS/LM/domain strings.

## Dependencies

This file depends on SMB request decode/encode helpers, session fields, server config, legacy and extended SMB authentication helpers, native OS/LanMan classification, request-specific memory, SMB token/idmap headers, and DTrace probes.

## Notable Invariants And Risks

- Password buffers are zeroed in post-processing before request storage is freed.
- Extended-security requests must advertise `CAP_EXTENDED_SECURITY`.
- `NT_STATUS_MORE_PROCESSING_REQUIRED` is encoded as an SMB status but is not treated as fatal.
- Required SMB3 encryption disables SMB1 session setup entirely.
- First-call detection for extended security uses `smb_uid == 0` or `0xFFFF`; follow-up calls preserve existing session properties.
- Native OS/LanMan strings are not security-critical and parsing is intentionally forgiving.
