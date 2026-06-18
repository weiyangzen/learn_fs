# sources/user-network-fs/samba/source4/lib/policy/wscript_build

This Waf script builds the Group Policy library and Python module. `bld.SAMBA_LIBRARY('samba-policy')` compiles `gp_ldap.c`, `gp_filesys.c`, `gp_manage.c`, and `gp_ini.c`, installs `samba-policy.pc`, exposes `policy.h`, and declares public dependencies on `ldb` and `samba-net`. `bld.SAMBA_PYTHON('py_policy')` builds `pypolicy.c` as `samba/policy.so` and links against `samba-policy` and pytalloc utility support.

Its main integration role is packaging the LDAP, SYSVOL, management, and INI helpers into one library. There is no runtime state. Risks are dependency drift, especially because `gp_filesys.c` uses SMB client APIs and `gp_manage.c` uses security descriptor helpers that must arrive transitively. Test signals are Waf target build, pkg-config generation, Python import of `samba.policy`, and link tests for external `policy.h` consumers.
