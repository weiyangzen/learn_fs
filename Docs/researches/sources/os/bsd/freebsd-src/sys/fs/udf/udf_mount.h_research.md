# File Research: sources/os/bsd/freebsd-src/sys/fs/udf/udf_mount.h

UDF mount flag definition header.

Key responsibilities:
- Defines `UDFMNT_KICONV`, the mount flag enabling kernel iconv-based filename conversion.

Dependencies:
- Consumed by UDF mount and vnode code when parsing `flags`, `cs_disk`, and `cs_local` options.

Notable risks:
- This is a very small ABI/option surface; flag value changes must remain compatible with mount tooling and kernel option parsing.
