# sources/user-network-fs/samba/source3/client/smbspool.c

## Purpose
`smbspool.c` is Samba's SMB backend for CUPS. It parses CUPS backend invocations and `smb://` device URIs, obtains credentials from URI or environment, connects to an SMB print share, and streams the print job as a remote spool file.

## Important APIs, Types, And Functions
- `main()` handles CUPS argument forms, `DEVICE_URI`, `AUTH_USERNAME`, `AUTH_PASSWORD`, `AUTH_INFO_REQUIRED`, file/stdin selection, URI parsing, Samba client initialization, retry behavior, and print submission.
- `get_exit_code()` maps selected NTSTATUS authentication failures to CUPS backend exit code `2` and prints `ATTR: auth-info-required=...`.
- `list_devices()` emits the generic SMB network printer backend line for CUPS discovery.
- `smb_connect()` chooses anonymous, username/password, Kerberos, or fallback authentication based on `auth_info_required` and available credential cache.
- `smb_complete_connection()` performs `cli_start_connection()`, `cli_session_creds_init()`, `cli_session_setup_creds()`, and `cli_tree_connect_creds()`.
- `kerberos_ccache_is_valid()` checks the default Kerberos credential cache and logs the principal.
- `smb_print()` sanitizes the job title, opens a spool file on the remote print share, streams data with `cli_writeall()`, and closes it.
- `uri_unescape_alloc()` talloc-duplicates and RFC1738-unescapes URI tokens.

## Control Flow
With no arguments, the backend lists devices and exits successfully. For print jobs, `main()` determines which argv slot contains the device URI and which slots contain CUPS job user/title/copies/file. It opens the input file or uses stdin, prefers `DEVICE_URI` over sanitized argv URIs, validates the `smb://` scheme, and parses optional credentials, workgroup, server, port, and printer. Samba logging, locale, configuration, interfaces, and transports are initialized. The backend retries connection failures up to `MAX_RETRY_CONNECT` except for authentication-required status or printer classes. After connecting, it ignores `SIGTERM` for stdin jobs, calls `smb_print()` once per requested copy, shuts down the CLI, frees global state, and returns the CUPS status.

`smb_connect()` first interprets `AUTH_INFO_REQUIRED`. `negotiate` requires a valid ccache and uses the CUPS job user for Kerberos. `username,password` requires a username and permits fallback after Kerberos. `samba` auto-selects username/password if provided or Kerberos if a ccache exists. On Kerberos failure, it may try passwordless NTLMSSP as the effective user and finally anonymous.

## State And Persistence
The file reads environment variables, local Samba configuration, local passwd data, and optional print input files. It opens a network connection, creates/truncates a remote spool file named from the sanitized job title, writes print data, and closes the remote handle to submit the job. It does not maintain local persistent state beyond normal Samba library caches and output to CUPS stderr/stdout conventions.

## Dependencies And Integration Points
The backend integrates with CUPS backend calling conventions and exit codes, Samba loadparm/client stack, SMB transport selection, Kerberos wrappers, talloc stack frames, and libsmb client functions. It expects `smbspool_krb5_wrapper` or cupsd to supply usable `KRB5CCNAME` for negotiate authentication.

## Risks
- URI parsing is manual and bounded by a 1024-byte local buffer; overlong URIs fail, but edge cases around escaped separators remain important.
- `smb_complete_connection()` passes `true` for `use_kerberos` from the main path even when `smb_connect()` computed `use_kerberos`; fallback flags influence behavior but this deserves regression coverage.
- Title sanitization only allows alnum and whitespace and rejects truncation, but title-to-remote-spool naming still depends on server behavior.
- Rewinding input for multiple copies works for files but stdin is forced to one copy.
- Kerberos cache validation proves a principal exists, not that a service ticket for the target server is usable.
- Authentication error mapping determines whether CUPS holds jobs for credentials; missing status values can produce retry loops instead of auth prompts.

## Test Signals
Run backend invocation permutations for argc 1, 5-8, URI in argv[0]/argv[1]/environment, with and without input files. Exercise `AUTH_INFO_REQUIRED` values `none`, `username,password`, `negotiate`, `samba`, unknown, and absent. Mock or integration-test connection failures, authentication failures, class retry behavior, multiple copies, long URIs, escaped credentials, port parsing, and write/close failures.
