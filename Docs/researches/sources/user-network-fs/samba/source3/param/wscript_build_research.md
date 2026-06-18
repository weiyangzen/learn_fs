# sources/user-network-fs/samba/source3/param/wscript_build

Purpose: declares build targets for Samba3 parameter utilities, S3 loadparm bridge, generated prototypes, Python bindings, service resolver, and `test_lp_load`.

Important build API: defines `PARAM_UTIL`, `LOADPARM_CTX`, `s3_param_proto_h` generator from `generate_param.py` and XML parameter metadata, Python module `pys3param`, Python utility subsystem `pyparam3_util`, `param_service`, and non-installed test binary `test_lp_load`.

State and persistence: no runtime state; generates `param_proto.h` during build and controls whether Python extension helpers are built.

Dependencies and integration: ties param code to `talloc`, `smbconf`, `samba-hostconfig`, Python embedding libraries, `USER_UTIL`, and `CMDLINE_S3`. The generated header keeps C prototypes synchronized with XML parameter definitions.

Risks: Python build gating must match consumers; missing generated header inputs can break broad source3 builds. Dependency under-declaration can surface only in clean or differently configured builds.

Test signals: clean Waf configure/build with Python enabled and disabled, generated `param_proto.h` freshness, import of `samba/samba3/param.so`, and execution of `test_lp_load`.
