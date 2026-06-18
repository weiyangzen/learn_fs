<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/ioctl_dm.c -->
# sources/test-tools/strace/tests/ioctl_dm.c

Purpose: `ioctl_dm.c` large device-mapper DM_* ioctl decoder test covering header validation, nested target specs/messages, strings, flags, and verbose truncation. This is the primary implementation body; no wrapper macros are layered on top of the source beyond its own defaults.

Important APIs/types/functions: Primary APIs and data surfaces are DM_VERSION, DM_REMOVE_ALL, DM_LIST_DEVICES, DM_LIST_VERSIONS, DM_DEV_CREATE/REMOVE/STATUS/WAIT/SUSPEND/ARM_POLL/SET_GEOMETRY/RENAME, DM_TABLE_CLEAR/DEPS/STATUS/LOAD, DM_TARGET_MSG, struct dm_ioctl, dm_target_spec, dm_target_msg. Local include directives/macros observed in this source are `tests.h, errno.h, inttypes.h, stdio.h, stddef.h, string.h, sys/ioctl.h, linux/ioctl.h, linux/dm-ioctl.h` and `STR32="AbCdEfGhIjKlMnOpQrStUvWxYz012345", ALIGNED_SIZE=(s_, t_) \, ALIGNED_OFFSET=(t_, m_) \, FILL_DM_TARGET=(id, id_next) \, PRINT_DM_TARGET=(id) \`. Locally visible function entry points include `init_s, init_dm_target_spec, print_dm_target_spec, main`.

Control flow: helper init_s seeds dm_ioctl headers and init_dm_target_spec builds deterministic targets. main exercises invalid operations, unsupported ABI versions, short data sizes, unterminated names/uuids, flag decoding, nodev/dev commands, table-load target walking, invalid data_start/next values, target messages, geometry strings, rename strings, and final overlarge target_count. For wrapper sources, preprocessing first applies the listed macros and then compiles the included base body; runtime control flow is therefore inherited from `ioctl_dm.c` with only the selected xlat, verbosity, injection, pid namespace, or string-length behavior changed.

State and persistence behavior: uses global struct s plus tail-allocated dm_ioctl layouts; no persistent state. VERBOSE controls whether nested target/message/string payloads are expanded or replaced with ellipses. The tests intentionally avoid durable state; they rely on deterministic local buffers, tail-page allocation, raw syscall/ioctl return capture, and expected-output printing for the strace test harness.

Dependencies and integration points: tests.h, linux/dm-ioctl.h, sys/ioctl.h, alignment macros, str129 fixture string, VERBOSE macro. Integration is through strace's testsuite: the compiled binary prints the expected trace, the shell harness or test runner captures strace output, and reconciliation compares symbolic ioctl/syscall decoder output against these expectations.

Risks: DM UAPI layout/flag drift, alignment assumptions, max string length truncation, and verbose/non-verbose split can break expected text. Wrapper files add risk that the include chain, macro value, or test name drifts from the harness entry that invokes it, producing correct C but mismatched expected output.

Test signals: Exact EBADF output checks header field selection, flag xlat expansion, safe traversal of nested variable-length data, inaccessible pointer reporting, and verbose ellipsis behavior. This file has 749 source lines and 24560 bytes; non-empty generated research at the mirrored `Docs/researches/sources/test-tools/strace/tests/ioctl_dm.c_research.md` path is the worker-produced signal for this source item.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/ioctl_dm.c -->
