<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/finit_module/finit_module.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/finit_module/finit_module.c

Purpose: Tiny kernel module fixture whose init/exit paths allow `finit_module` syscall tests to load a known module object. Source notes: Dummy test module. The module accepts a single argument named "status" and it fails initialization if the status is set to "invalid". SPDX-License-Identifier: GPL-2.0-or-later The file was read in full for this report (39 lines, 780 bytes).

Important APIs/types/functions: types/structs: struct proc_dir_entry; functions: dummy_init, dummy_exit; local macros/constants: DIRNAME.

Control flow: setup path: dummy_init; cleanup path: dummy_exit.

State and persistence behavior: The test manipulates kernel module load/unload state. Cleanup and SAFE_* wrappers are responsible for closing descriptors, unmapping memory, restoring tunables, removing temporary files, and reaping children where applicable.

Dependencies and integration points: includes `linux/module.h`, `linux/init.h`, `linux/proc_fs.h`, `linux/kernel.h`; integrates with the LTP finit_module syscall suite.

Risks: kernel config, module signing, and privilege policy affect results.

Test signals: errno checks: EINVAL.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/finit_module/finit_module.c -->
