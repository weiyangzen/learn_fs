# sources/user-network-fs/samba/source3/utils/wscript_build

## Purpose

`sources/user-network-fs/samba/source3/utils/wscript_build` is the Waf build manifest for many Samba source3 utility binaries and utility subsystems. It declares sources, dependencies, install behavior, feature gates, and conditional source composition for tools such as `smbpasswd`, `smbtree`, `testparm`, `smbstatus`, `net`, `mdsearch`, and `wspsearch`. The source was read as a complete 373-line file.

## Important APIs, Types, and Functions

The file uses build DSL calls including `bld.SAMBA3_SUBSYSTEM`, `bld.SAMBA3_BINARY`, `bld.SAMBA_BINARY`, `bld.SAMBA3_PYTHON`, `bld.CONFIG_GET`, and `bld.CONFIG_SET`. Important local build variable `smbstatus_source` conditionally appends `status_profile.c` or `status_profile_dummy.c`, and `status_json.c` or `status_json_dummy.c`.

## Control Flow

At Waf configure/build time, the script registers subsystems first, then many binaries with multiline dependency lists. Conditional build gates enable `samba-regedit`, `mvxattr`, `smb_prometheus_endpoint`, and `wspsearch` only under corresponding environment/config flags. `smbstatus` source list is assembled based on `WITH_PROFILE` and `HAVE_JANSSON`.

## State and Persistence Behavior

The file does not own runtime state. It affects build graph state by registering targets, dependency edges, install paths, and source selections.

## Dependencies and Integration Points

It connects utility source files to Samba libraries such as `smbconf`, `CMDLINE_S3`, `cmdline_contexts`, `pdb`, `PASSWD_UTIL`, `PASSCHANGE`, `smbclient`, `msrpc3`, `LOCKING`, `PROFILE`, `CONN_TDB`, `jansson`, `common_auth`, WSP libraries, and Python embedding libraries.

## Risks and Edge Cases

Dependency omissions surface as link or runtime feature failures. Conditional dummy/real source selection for `smbstatus` must match C preprocessor expectations around Jansson/profile support. Feature-gated tools like `wspsearch` can silently disappear from builds when environment flags are false.

## Test Signals

Build matrix tests should cover profile on/off, Jansson on/off, WSP enabled/disabled, optional regedit/mvxattr/prometheus settings, and link-time coverage for each declared binary.
