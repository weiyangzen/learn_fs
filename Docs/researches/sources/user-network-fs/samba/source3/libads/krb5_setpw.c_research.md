# sources/user-network-fs/samba/source3/libads/krb5_setpw.c

## Purpose
`krb5_setpw.c` implements Kerberos password set/change flows for ADS: setting another principal's password using an existing ccache and changing the authenticating principal's own expired/current password using raw initial credentials.

## Important APIs and Functions
Public functions under `HAVE_KRB5` are `ads_krb5_set_password` and `kerberos_set_password`. Internal helpers are `kpasswd_err_to_krb5_err`, `kerb_prompter`, and `ads_krb5_chg_password`.

## Control Flow and Behavior
`ads_krb5_set_password` requires a ccache name, initializes Kerberos, optionally parses a target principal, resolves the ccache, calls `krb5_set_password_using_ccache`, maps kpasswd result codes, and cleans up principal, ccache, and context. `ads_krb5_chg_password` parses the principal, configures short-lived non-forwardable/proxiable initial creds for `kadmin/changepw@REALM`, adds a NetBIOS Kerberos address to avoid Heimdal local-address issues, obtains initial creds with the old password and custom prompter, then calls `krb5_set_password`. `kerberos_set_password` chooses the own-password change path when auth and target principals match; otherwise it creates a unique memory ccache, kinit's as the auth principal, and sets the target password through that ccache.

## State and Persistence
Password changes persist on the KDC/AD. The different-principal path creates and destroys a temporary memory credential cache. No local durable files are written by this file.

## Dependencies and Integration Points
It depends on Kerberos libraries, Samba Kerberos wrappers, `kerberos_kinit_password`, ADS status mapping, NetBIOS name configuration, and ASN.1 include infrastructure. It integrates with password change tools and domain administration flows.

## Risks and Test Signals
Kpasswd result mapping is lossy but maps common policy/access/principal/enctype failures. The own-password path intentionally avoids ccache use and relies on service principal canonicalization behavior that differs between MIT and Heimdal; MIT canonicalization is disabled in a documented bug block. Sensitive old/new passwords should not be logged. Tests should cover same-principal vs admin-set paths, missing ccache, bad old password, policy reject, unknown principal, ccache creation/destruction, kadmin/changepw realm construction, and MIT/Heimdal conditional behavior.
