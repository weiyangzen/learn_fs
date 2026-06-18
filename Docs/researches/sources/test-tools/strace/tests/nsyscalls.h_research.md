<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/nsyscalls.h -->
# sources/test-tools/strace/tests/nsyscalls.h

Purpose: validates strace decoding of helper header for nsyscalls using synthetic syscall or netlink inputs with deterministic expected output.

Important APIs/types/functions: covers `syscallent` table inclusion, `out_of_range_syscall_args`, `invoke_syscall` wrapper with `SYSCALL_BIT`. The fixture uses strace test helpers such as `tests.h`, `test_nlattr.h`, `scno.h`, `sprintrc`, allocation helpers, xlat macros, and Linux UAPI structs/constants relevant to this decoder surface.

Control flow: initializes a representative message or syscall argument block, fills deterministic byte patterns, executes positive semantic decode cases and unknown/fallback cases, prints the exact expected strace output, and exits with the standard success marker.

State/persistence behavior: these tests do not persist application state beyond temporary trace fixtures. They allocate synthetic netlink/syscall argument buffers with test helpers, may create or remove short-lived files or sockets, print the expected strace line to stdout, and terminate with `+++ exited with 0 +++` when the decoder behavior matches the fixture contract.

Dependencies/integration points: depends on architecture/kernel feature guards, relevant Linux UAPI headers, proc fd availability for fd/path-aware cases, and the strace decoder selected by syscall number, netlink family, message type, and nested attribute type. Source includes observed: #include "tests.h"; #include "sysent.h"; #include "scno.h"; #include <errno.h>; #include <stdio.h>; #include <stdlib.h>; #include <unistd.h>; #include "sysent_shorthand_defs.h"; ... (10 total).

Risks: UAPI growth can turn unknown cases into known symbolic output; struct-size changes can affect cropped/full payload behavior; endian and xlat mode differences can change expected text. Feature-gated legacy syscalls may skip on unsupported architectures.

Test signals: useful signals include successful compilation under the target guard, expected known/unknown xlat names, stable escaped byte output for truncated payloads, correct ifindex/fd/path annotation, and final `+++ exited with 0 +++`. Source-read signal: `sources/test-tools/strace/tests/nsyscalls.h` has 46 source lines in this checkout, and this report preserves the source-tree-aligned path for reconciliation.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/nsyscalls.h -->
