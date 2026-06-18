# sources/user-network-fs/samba/source3/auth/auth_builtin.c

## Purpose
This file provides built-in auth modules that do not require external identity stores. The main production module is `anonymous`, which accepts empty anonymous credentials and constructs anonymous server info.

## Important APIs, Types, and Functions
`check_anonymous_security` implements the module. `auth_init_anonymous` creates an `auth_methods` record named `anonymous`. Under `DEVELOPER`, `check_name_to_ntstatus_security` and `auth_init_name_to_ntstatus` expose a testing backend that maps usernames to NTSTATUS values. `auth_builtin_init` registers available built-ins.

## Control Flow
The anonymous checker only handles empty mapped account names. It rejects non-empty plaintext, non-null hashes, non-empty NT responses, and LM responses other than empty or single NUL by returning `NT_STATUS_NOT_IMPLEMENTED`, allowing later modules to try. If the input is genuinely anonymous, it calls `make_server_info_anonymous`.

## State and Persistence
No persistent state is stored. Anonymous server-info construction depends on cached anonymous/guest session state initialized elsewhere in `auth_util.c`.

## Dependencies and Integration Points
The file depends on `auth.h`, string helpers, the auth backend registration API in `auth.c`, and server-info constructors. It is normally first in the auth chain so anonymous handling is centralized before SAM or winbind.

## Risks and Test Signals
The critical risk is classifying credential blobs correctly: a malformed but non-empty response must not become anonymous. Tests should cover empty username with empty plaintext/hash/response combinations, non-empty username fallback, developer-only NTSTATUS mapping, and behavior when anonymous cached session info has not been initialized.
