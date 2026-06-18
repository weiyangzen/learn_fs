<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/auth/wscript_build -->
# sources/user-network-fs/samba/source3/auth/wscript_build

## Purpose
Defines the Waf build graph for the source3 authentication subsystem, including utility subsystems, the private `auth` library, and built-in or optional authentication modules.

## APIs, Types, and Functions
The script calls `bld.SAMBA3_SUBSYSTEM()` for `TOKEN_UTIL`, `USER_UTIL`, and `AUTH_COMMON`; `bld.SAMBA3_LIBRARY()` for the private `auth` library; and `bld.SAMBA3_MODULE()` for `auth_sam`, `auth_unix`, `auth_winbind`, `auth_builtin`, and `auth_samba4`. It lists source files and dependency strings rather than runtime APIs.

## Control Flow, State, and Persistence
At configure/build time, Waf evaluates these declarations to decide compilation units, library/module boundaries, dependencies, and enablement. `TOKEN_UTIL` builds from `token_util.c`; `USER_UTIL` builds from `user_util.c` and depends on `TOKEN_UTIL`; `AUTH_COMMON` groups common auth helpers including `server_info_sam.c` and `user_info.c`; the private `auth` library includes `user_krb5.c` and NTLMSSP/generic auth sources. Module enablement is conditional for `auth_unix` and `auth_samba4` based on Samba static-module and AD DC build settings.

## Dependencies and Integration
The declared dependencies connect auth code to `samba-util`, passdb (`pdb`), DC utilities, common auth code, plaintext auth, credential/cache helpers, Netlogon client code, hostconfig, messaging, and Samba4 auth/gensec libraries for the `auth_samba4` module. This file is the build integration point that determines whether the source files researched in this group are linked into subsystems, a private library, or modules.

## Risks and Test Signals
Risks include missing dependency declarations causing link failures, moving functions between files without updating subsystem deps, static/dynamic module condition drift, and AD DC builds excluding or including `auth_samba4` incorrectly. Test signals are clean Waf configure/build for static and shared modules, builds with and without AD DC support, builds with `auth_unix` disabled, and link coverage for `TOKEN_UTIL`, `USER_UTIL`, `AUTH_COMMON`, and the private `auth` library.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/auth/wscript_build -->
