<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/nsfs.c -->
# sources/test-tools/strace/src/nsfs.c

Purpose: decodes namespace filesystem ioctl commands.

Important APIs/types/functions: `nsfs_ioctl`, `print_mnt_ns_info`, `struct mnt_ns_info`, and `NS_*` ioctl constants.

Control flow: returns fd-formatted results for namespace fd getters, decodes `NS_GET_NSTYPE` return aux strings, prints owner uid, namespace ids, PID/TGID translations, and mount namespace info for variable-sized `NS_MNT_GET_*` ioctls.

State and persistence behavior: no persistent state in this file; it reads ioctl output buffers on exit and sets `tcp->auxstr` for namespace type names.

Dependencies and integration points: used by the generic ioctl dispatcher; depends on `<linux/nsfs.h>`, pid printers, uid printers, `setns_types`, and ioctl size macros.

Risks: many commands are exit-only because output buffers are valid after syscall completion. Size-gated mount namespace ioctls must track kernel structure versions.

Test signals: `NS_GET_USERNS`, `NS_GET_PARENT`, `NS_GET_NSTYPE`, owner uid, mount namespace info/prev/next, PID namespace id translations, short ioctl sizes, and syscall failures.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/nsfs.c -->
