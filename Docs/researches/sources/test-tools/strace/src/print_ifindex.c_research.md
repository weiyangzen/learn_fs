<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/print_ifindex.c -->
# sources/test-tools/strace/src/print_ifindex.c

Purpose: prints network interface indexes, optionally annotated with interface names.

Important APIs/types/functions: `get_ifname`, `print_ifindex`, `sprint_ifname`, `if_indextoname`, and string quoting helpers.

Control flow: when `HAVE_IF_INDEXTONAME` is available, resolves the index to an interface name, quotes it, and prints as `if_nametoindex("name")` using xlat formatting; otherwise prints the numeric index.

State and persistence behavior: uses static buffers for resolved names and formatted strings; no persistent cache.

Dependencies and integration points: used by netlink, socket, multicast, and NUMA-related printers; depends on `<net/if.h>` and xlat verbosity.

Risks: static buffers are overwritten on subsequent calls. Interface names depend on the strace process namespace, which may not match the tracee.

Test signals: existing and nonexistent ifindexes, quoted names with special characters, fallback builds without `if_indextoname`, and xlat verbosity modes.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/print_ifindex.c -->
