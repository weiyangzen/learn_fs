<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/utils/ntlm_auth.c -->
# sources/user-network-fs/samba/source3/utils/ntlm_auth.c

## Purpose

`ntlm_auth.c` implements Samba's `ntlm_auth` command and stdio helper. It authenticates plaintext passwords, NTLM challenge/response blobs, Squid helper exchanges, NTLMSSP client/server handshakes, SPNEGO/GSS handshakes, and password-change helper requests. The file is both a command-line utility and a long-lived line-oriented protocol worker used by external programs.

## Important APIs, Types, and Functions

The central state is `struct ntlm_auth_state`, which preserves helper mode, client state, GENSEC/NTLMSSP state, requested feature strings, session-key state, and private protocol state across stdin lines. `stdio_helper_protocols[]` maps externally visible helper protocol names to handler functions. Public helpers exported through `ntlm_auth_proto.h` include `get_winbind_domain()`, `get_winbind_netbios_name()`, `get_challenge()`, `contact_winbind_auth_crap()`, and `get_pam_winbind_config()`.

Important internal paths include `check_plaintext_auth()` for `WINBINDD_PAM_AUTH`, `contact_winbind_auth_crap()` for `WINBINDD_PAM_AUTH_CRAP`, `contact_winbind_change_pswd_auth_crap()` for encrypted password changes, `make_auth4_context_ntlm_auth()` for GENSEC password checking, `ntlm_auth_prepare_gensec_client()` and `ntlm_auth_prepare_gensec_server()` for SPNEGO/NTLMSSP setup, and `manage_gensec_request()` for most token-based helper protocols.

## Control Flow

`main()` initializes Samba cmdline/loadparm state, parses options, derives domain/user defaults, opens a loadparm context, and then either starts a persistent helper stream or performs a one-shot authentication. Helper mode enters `squid_stream()`, which repeatedly calls `manage_squid_request()` to assemble one newline-delimited request up to `MAX_BUFFER_SIZE` and dispatch to the selected handler.

Basic helper requests split `user password`, optionally RFC1738-decode Squid 2.5 input, and call `check_plaintext_auth()`. GENSEC helpers accept prefixes such as `YR`, `TT`, `KK`, `AF`, `NA`, `PW`, `GK`, `GF`, and `SF`; they lazily create client or server GENSEC state, decode base64 tokens, call `gensec_update()`, squash authentication errors, and print Squid-compatible response codes. `NTLM_SERVER_1` and `NTLM_CHANGE_PASSWORD_1` accumulate key/value request lines in static variables until `.` commits the transaction, then reset the static request state.

## State and Persistence Behavior

The process holds option globals for username/domain/workstation/password, response blobs, membership requirements, cached/offline flags, and target SPN fields. Winbind details and generated challenges are cached in static variables. Long-lived helpers retain GENSEC state across lines. Authentication itself is delegated to winbind and does not persist local account data, except password-change requests forwarded to winbind can mutate account passwords. Sensitive plaintext and hashes are partially zeroed in some paths, but many values live in talloc allocations or static request variables until reset.

## Dependencies and Integration Points

The file integrates with libwbclient/winbindd private requests, GENSEC, NTLMSSP, SPNEGO, Kerberos PAC parsing when available, Samba credentials/loadparm/cmdline libraries, tiniparser for `pam_winbind.conf`, base64/hex utilities, GnuTLS ARCFOUR for password-change blob encryption, and diagnostics in `ntlm_auth_diagnostics.c`.

## Risks and Edge Cases

The helper protocols are external compatibility contracts; output prefixes and newline framing are fragile. Several helper transactions use static variables, which is acceptable for single-threaded stdin helpers but unsuitable for concurrent dispatch. `manage_ntlm_change_password_1_request()` has subtle blob-presence checks and a reset typo that assigns `old_nt_hash_enc` twice instead of clearing `old_lm_hash_enc`. Some request blob copies assume validated fixed lengths, while winbind auth caps or allocates large NTLMv2 responses. Password material moves through stdout prompts, talloc, static buffers, and GnuTLS state, so memory-lifetime review matters.

## Test Signals

Useful tests are Squid basic/NTLMSSP protocol transcripts, GSS-SPNEGO client/server token exchange tests, challenge/response one-shot auth with and without session-key requests, membership restriction tests using name and SID forms, offline/cached credential paths, FIPS/ARCFOUR password-change failures, and diagnostics mode against servers with and without LM support.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/utils/ntlm_auth.c -->
