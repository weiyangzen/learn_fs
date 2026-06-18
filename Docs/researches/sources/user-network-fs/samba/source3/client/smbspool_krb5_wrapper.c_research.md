# sources/user-network-fs/samba/source3/client/smbspool_krb5_wrapper.c

## Purpose
`smbspool_krb5_wrapper.c` is a privileged CUPS backend helper for Kerberos printing. It decides whether Kerberos negotiation is required, switches from root to the authenticated CUPS user's uid/gid when necessary, preserves or discovers a Kerberos credential cache, sanitizes the environment, and execs the real `smbspool` binary.

## Important APIs, Types, And Functions
- `cups_smb_debug()` emits CUPS-style `DEBUG:` or `ERROR:` messages.
- `kerberos_get_default_ccache()` initializes Kerberos, resolves Samba's forced default ccache name, obtains the full cache name, and copies it into the caller buffer.
- `main()` is the wrapper driver handling `DEVICE_URI`, `AUTH_INFO_REQUIRED`, `AUTH_UID`, privilege changes, `KRB5CCNAME`, environment cleanup, and `execv()`.

## Control Flow
The wrapper saves `DEVICE_URI`, reads `AUTH_INFO_REQUIRED`, and immediately delegates to `smbspool` for absent, `none`, `username,password`, or unrecognized authentication modes. Only `negotiate` activates Kerberos-specific handling. If already non-root, or if `AUTH_UID` maps to root, it delegates directly. Otherwise it validates and converts `AUTH_UID`, looks up the passwd entry, clears supplementary groups, adds the `lp` group so the job file remains accessible, switches gid then uid, chooses `KRB5CCNAME` from the existing environment, the Kerberos default cache, or `FILE:/tmp/krb5cc_<uid>`, clears the environment, restores only needed variables, and execs `${BINDIR}/smbspool` with the original argv.

## State And Persistence
The wrapper mutates process credentials and environment before `execv()`. It does not write files itself, but it may point `KRB5CCNAME` at an existing or conventional file cache path. Failure returns CUPS backend status codes such as `CUPS_BACKEND_AUTH_REQUIRED` or `CUPS_BACKEND_FAILED`.

## Dependencies And Integration Points
It integrates with CUPS backend headers and status codes, Samba dynconfig for `get_dyn_BINDIR()`, Kerberos libraries, system passwd/group APIs, `setgroups()`, `setgid()`, `setuid()`, and the downstream `smbspool` backend.

## Risks
- `CUPS_SMB_ERROR` is defined with `CUPS_SMB_LOG_DEBUG`, so error messages may be labeled `DEBUG` rather than `ERROR`.
- It assumes a local `lp` group is required and present; systems using a different CUPS spool group will fail.
- `strtoul(env, NULL, 10)` does not validate full-string consumption, so partially numeric `AUTH_UID` strings can be accepted.
- `execv()` failure returns its negative value directly without a CUPS-specific diagnostic path.
- The fallback `FILE:/tmp/krb5cc_<uid>` may not exist or may be inaccessible after environment cleanup.

## Test Signals
Test each `AUTH_INFO_REQUIRED` branch, root and non-root execution, missing/invalid/partial `AUTH_UID`, absent `lp` group, uid/gid switch failures, existing `KRB5CCNAME`, default ccache discovery, Heimdal/MIT free paths, environment sanitization, and `execv()` failure. Packaging tests should verify installation permissions and backend symlink layout.
