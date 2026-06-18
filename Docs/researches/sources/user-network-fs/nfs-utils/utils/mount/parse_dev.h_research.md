# sources/user-network-fs/nfs-utils/utils/mount/parse_dev.h

Purpose: declares the NFS device-name parser.

Important API: `int nfs_parse_devname(const char *, char **, char **);` returns success/failure and optionally allocates hostname and pathname output strings.

Control flow and integration: consumers include this to split `host:dir` or `[IPv6]:dir` syntax before address resolution or unmount advisory processing.

State and persistence: no state; callers own and must free allocated output values from the implementation.

Dependencies: no includes are required by the prototype.

Risks and tests: the header gives no ownership note, so callers must learn allocation behavior from implementation. Test signals are compile coverage and parser tests for all supported/unsupported device forms.
