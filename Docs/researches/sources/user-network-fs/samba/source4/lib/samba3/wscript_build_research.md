# sources/user-network-fs/samba/source4/lib/samba3/wscript_build

## Purpose

This `wscript_build` declares the source4 Samba3 smbpasswd parser helper library.

## Important APIs, Types, and Functions

It contains one `SAMBA_LIBRARY('smbpasswdparser')` declaration with `source='smbpasswd.c'`, dependency `samba-util`, and `private_library=True`.

## Control Flow

At waf build time, the declaration compiles `smbpasswd.c` into a private library. There is no runtime control flow.

## State and Persistence Behavior

The build rule has no runtime state. It controls artifact availability for code that needs smbpasswd hash parsing/formatting helpers.

## Dependencies and Integration Points

The only declared build dependency is `samba-util`, which supplies hex conversion and common utility support used by `smbpasswd.c`.

## Risks and Edge Cases

Because the library is private and very small, consumers must be in-tree. Missing generated SAMR include dependencies are satisfied indirectly by source includes rather than explicit build deps here.

## Test Signals

Successful build of `smbpasswdparser` and unit coverage of `smbpasswd_gethexpwd()`/`smbpasswd_sethexpwd()` are the relevant signals.

Source-read signal: reviewed complete local file (9 lines).
