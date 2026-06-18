# sources/user-network-fs/samba/source4/ntvfs/unixuid/wscript_build

Purpose: This Waf script builds the `ntvfs_unixuid` pass-through module.

Important APIs, types, and functions: It declares `bld.SAMBA_MODULE('ntvfs_unixuid', source='vfs_unixuid.c', subsystem='ntvfs', init_function='ntvfs_unixuid_init', deps='auth_unix_token talloc')`.

Control flow: The script has a single module declaration. It is reached from the parent NTVFS build only when `WITH_NTVFS_FILESERVER` is enabled.

State and persistence behavior: No runtime state is in the script. It determines whether the credential-switching wrapper can be loaded as an NTVFS module.

Dependencies and integration points: It links with Unix token conversion and talloc. The module registers with the NTVFS subsystem under `unixuid`.

Risks: Missing `auth_unix_token` support prevents the module from building, which changes the server's ability to enforce filesystem access using Unix credentials.

Test signals: Build and module-load tests should ensure `ntvfs_unixuid_init` is present and the module appears in NTVFS registration when file server support is enabled.
