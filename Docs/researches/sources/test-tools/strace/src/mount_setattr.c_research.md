<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/mount_setattr.c -->
# sources/test-tools/strace/src/mount_setattr.c

Purpose: decodes modern mount API calls `mount_setattr`, `open_tree`, and `open_tree_attr`.
Important APIs/types/functions: `print_mount_attr`, `decode_dfd_file_flags`, `decode_dfd_file_flags_attr`, `mount_attr_attr`, `mount_attr_propagation`, `mount_setattr_flags`, and `open_tree_flags`.
Control flow: validates `mount_attr` size, fetches bounded known fields, prints idmap user namespace fd only when relevant, emits future nonzero bytes, and shares dirfd/path/flags printing across syscalls.
State and persistence behavior: stateless. Dependencies and integration points: Linux mount API syscall table and fd/path helpers.
Risks: versioned structure growth and conditional fd interpretation are easy to misprint. Test signals: minimum/oversized attr, idmapped mounts, open_tree flags, and invalid small size cases.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/mount_setattr.c -->
