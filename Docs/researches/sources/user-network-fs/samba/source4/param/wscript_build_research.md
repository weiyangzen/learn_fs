# sources/user-network-fs/samba/source4/param/wscript_build

Purpose: This Waf script builds Samba4 parameter/provision/share/secrets components and Python bindings.

Important APIs, types, and functions: It declares subsystems for embedded `PROVISION`, `share`, `SECRETS`, `pyparam_util`, and `param_options`; modules/libraries `share_classic`, Python extension `pyparam`, and grouping library `shares`.

Control flow: Python-enabled targets use `bld.pyembed_libname` for embedded Python, pytalloc, pyldb, and pyparam utility dependencies. The provision subsystem is enabled only when Python build support is enabled. Share and secrets subsystems are normal C targets, while `pyparam` installs as `samba/param.so`.

State and persistence behavior: The script has no runtime state. Build outcomes determine whether provisioning from C, Python loadparm bindings, share backend registration, secrets database helpers, and client option helpers are available.

Dependencies and integration points: It links to `samba-hostconfig`, `server-role`, `samba-debug`, `ldb`, `tdb-wrap`, `util_tdb`, `NDR_SECURITY`, `tevent`, and `ldbwrap`.

Risks: Python target names use embedded-library helper names, so Python-disabled builds omit provisioning glue. Dependency drift can break extension import at runtime despite successful C compilation.

Test signals: Build tests should cover Python enabled/disabled, import of `samba.param`, module registration of `share_classic`, and linkage of `SECRETS` and `param_options`.
