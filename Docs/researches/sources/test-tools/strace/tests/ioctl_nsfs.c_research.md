<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/ioctl_nsfs.c -->
# sources/test-tools/strace/tests/ioctl_nsfs.c

Purpose: tests generic namespace file descriptor ioctls: user namespace lookup, parent namespace lookup, namespace type, owner UID, and mount namespace id.

Important APIs/types/functions: Uses `test_no_namespace`, `test_clone`, `child`, `test_user_namespace`, `clone`/`__clone2`, `CLONE_NEWUSER`, `/proc/<pid>/ns/user`, `/proc/self/ns/mnt`, and `NS_GET_USERNS`, `NS_GET_PARENT`, `NS_GET_NSTYPE`, `NS_GET_OWNER_UID`, `NS_GET_MNTNS_ID`.

Control flow: first calls namespace ioctls on fd `-1` and optionally on current mount namespace. Then creates a child in a new user namespace using a pipe for lifetime control, opens the child's user namespace fd, queries userns/parent/type/owner uid, releases the child, and waits for clean exit.

State and persistence behavior: creates transient child process and user namespace; no persistent state. Namespace fds are opened and closed during the test.

Dependencies/integration points: requires clone/user namespace support, `/proc`, `linux/nsfs.h`, and strace's namespace type/uid/id decoders.

Risks and test signals: user namespace creation can be disabled, causing partial skip-like behavior. Passing output confirms nsfs command names, fd-return formatting, CLONE_NEWUSER type xlat, and owner UID pointer decoding.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/ioctl_nsfs.c -->
