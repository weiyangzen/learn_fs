<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/cifs-utils/cifs.idmap.c -->
# sources/user-network-fs/cifs-utils/cifs.idmap.c

## Purpose

`cifs.idmap.c` implements the request-key helper that maps CIFS owner/group SIDs to local UID/GID values and maps local UID/GID values back to binary SIDs for kernel CIFS ACL handling.

## Important APIs, Types, and Functions

Important functions are `usage`, `strget`, `str_to_uint`, `cifs_idmap`, and `main`. It uses `struct cifs_sid`, `struct cifs_uxid`, plugin entry points from `idmap_plugin.h`, and keyutils calls `keyctl_set_timeout`, `keyctl_describe_alloc`, and `keyctl_instantiate`.

## Control Flow

`main` parses `--timeout`, `--version`, and a key serial, initializes the ID mapping plugin, sets the key timeout, obtains the key description, and calls `cifs_idmap`. `cifs_idmap` inspects description substrings: `os:` maps owner string to SID then UID, `gs:` maps group string to SID then GID, `oi:` maps owner UID to SID, and `gi:` maps group GID to SID. Successful mappings instantiate the kernel key with either a `uid_t`, `gid_t`, or packed `struct cifs_sid`.

## State and Persistence Behavior

The helper has a process-global plugin handle and emits results into the kernel keyring. The key timeout defaults to 600 seconds but can be set to zero for no expiry. It does not persist data on disk.

## Dependencies and Integration Points

It depends on keyutils, syslog, `cifsacl.h`, `cifsidmap.h`, and the dynamically loaded idmap plugin configured by `IDMAP_PLUGIN_PATH`. It is normally invoked by request-key for `cifs.idmap` keys when CIFS mounts use `cifsacl`.

## Risks and Edge Cases

Description parsing uses substring searches rather than a strict grammar, so malformed descriptions can choose unintended branches. UID/GID parsing validates conversion and overflow, but casts through `unsigned int` before assigning to uid/gid carriers. Plugin failures must propagate correctly or the kernel may cache negative behavior. The allocated description buffer is not freed on the success path shown, which is small but worth noting.

## Test Signals

Tests should mock or provide an idmap plugin and exercise all four key-description forms, bad numeric values, timeout parsing, missing plugin symbols, key instantiation failures, and request-key integration. Winbind-backed integration should confirm SID endian correctness through `idmapwb.so`.
<!-- END_FILE_RESEARCH: sources/user-network-fs/cifs-utils/cifs.idmap.c -->
