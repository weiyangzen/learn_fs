# File Research: sources/os/bsd/netbsd-src/lib/libc/citrus/citrus_pivot_file.h

Read completely: 35 lines.

This header defines the serialized pivot database magic strings: `_CITRUS_PIVOT_MAGIC` as `CSPIVOT\0` and `_CITRUS_PIVOT_SUB_MAGIC` as `CSPIVSUB`.

It is shared between pivot DB writers and readers so the nested DB layers can validate file type.

Security/reliability notes: no executable code. Correct magic validation in consumers depends on these constants remaining synchronized with generated DB files.
