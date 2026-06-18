## sources/user-network-fs/libtirpc/src/clnt_perror.c

Purpose: Formats and prints RPC client and client-creation errors for legacy libtirpc APIs.

Important APIs and control flow: `_buf` lazily allocates one process-global 256-byte buffer. `clnt_sperror` fetches `CLNT_GETERR`, appends the base `clnt_sperrno` string, and adds status-specific detail for errno, version ranges, auth errors, or unknown low bits. `clnt_perror`, `clnt_perrno`, and `clnt_pcreateerror` print to stderr. `clnt_spcreateerror` formats `rpc_createerr`, including nested pmap failure details. `auth_errmsg` maps `enum auth_stat` values.

State and persistence: The static buffer is reused for all callers and is not thread-safe. It persists until process exit.

Dependencies and integration: Used by pmap helpers and applications calling traditional SunRPC error APIs. Depends on global or macro-resolved `rpc_createerr`.

Risks and test signals: Shared buffer reuse, truncation handling, and enum-range mismatches are the main risks. Tests should check every `enum clnt_stat`, auth-error detail, pmap/system errno formatting, null input handling, and concurrent callers if thread safety matters.
