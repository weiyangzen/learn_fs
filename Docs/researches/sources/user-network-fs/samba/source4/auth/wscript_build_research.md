# sources/user-network-fs/samba/source4/auth/wscript_build

Purpose: Waf build definitions for the source4 authentication components, tests, and Python auth module.

Important targets: recurses into `gensec`, `kerberos`, and `ntlm`; defines `auth_session`, private `auth_unix_token`, `samba_server_gensec`, `auth_system_session`, and `auth4_sam`; builds selftest binaries `test_kerberos`, `test_auth_sam`, and conditionally `test_heimdal_gensec_unwrap_des`; builds Python module `pyauth` as `samba/auth.so`.

Control flow/state: subsystem/library declarations specify source files, autoproto headers, public headers/dependencies, and private dependencies. Build metadata generates headers/products but stores no runtime state.

Dependencies/integration: connects this subset to Samba credentials, SAMDB, security, LDB, tevent, GENSEC, auth4, winbind client, Kerberos, Python embedding, and conditional Heimdal/system-GSSAPI config symbols. Tests use cmocka and linker wrap flags to isolate target functions.

Risks/test signals: dependency declarations shape ABI visibility and test availability. Conditional Heimdal test gating means DES unwrap regression coverage is absent with system GSSAPI or non-Heimdal builds. This file registers all three auth tests studied here.
