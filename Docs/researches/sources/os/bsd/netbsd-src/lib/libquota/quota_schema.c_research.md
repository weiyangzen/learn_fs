# File Research: sources/os/bsd/netbsd-src/lib/libquota/quota_schema.c

This file implements schema and capability inspection for quota handles. `quota_getimplname` reports `"nfs via rquotad"` for NFS, delegates oldfiles and kernel implementation names to their backends, and returns `EINVAL` for invalid mode.

`quota_getrestrictions` reports NFS as 32-bit and read-only, oldfiles as needing quotacheck with uniform grace and 32-bit values, and kernel restrictions from `__quota_kernel_getrestrictions`. `quota_getnumidtypes` returns two for NFS and oldfiles and delegates kernel mode. `quota_idtype_getname` delegates kernel mode, otherwise maps user/group to `"user"`/`"group"` and invalid ids to `"???"` with `EINVAL`.

Object-type helpers follow the same pattern. `quota_getnumobjtypes` returns two except for kernel delegation. `quota_objtype_getname` maps blocks to `"block"` and files to `"file"` unless kernel mode supplies names. `quota_objtype_isbytes` delegates kernel mode, otherwise reports block quotas as byte-like and file quotas as count-like.
