# sources/test-tools/syzkaller/pkg/csource/testdata/0

This syscall-generation fixture contains a two-call netlink program and its expected generated comments plus syscall bodies. The input opens a netlink socket and binds it to a `sockaddr_nl_t` with a group bitmap.

Important signals are resource flow from `socket$netlink` return value `r0` into `bind$netlink`, constant/flag annotation (`NETLINK_USERSOCK`), pointer address rendering, and translation from syzkaller call variants to native `__NR_socket` and `__NR_bind` syscalls. There is no executable state inside the file beyond fixture text.

The integration point is `syscall_generation_test.go`, which parses the program before the blank line and compares the stored comments/syscall lines after it. Risks are exact-format brittleness and target metadata changes affecting annotation names or numeric constants. Test signal is compact coverage of resource comments, struct field comments, native syscall names, and generated argument comments.
