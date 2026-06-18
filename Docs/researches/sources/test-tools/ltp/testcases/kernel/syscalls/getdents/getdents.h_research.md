<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/getdents/getdents.h -->
# sources/test-tools/ltp/testcases/kernel/syscalls/getdents/getdents.h

Purpose: the Free Software Foundation; either version 2 of the License, or (at your option) any later version. but WITHOUT ANY WARRANTY; without even the implied warranty of along with this program; if not, write to the Free Software See fs/compat.c struct compat_linux_dirent

Important APIs/types/functions: includes `stdint.h`, `config.h`, `lapi/syscalls.h`, `unistd.h`; touches `getdents`, `raw syscall path`; defines `linux_getdents`, `linux_getdents64`, `tst_getdents`, `getdents_info`.

Control flow centers on `linux_getdents`, `linux_getdents64`, `tst_getdents`, `getdents_info`.

State and persistence behavior: Runtime state is a directory file descriptor and the kernel getdents buffer containing linux_dirent records.

Dependencies and integration points: Depends on the LTP test framework, Linux syscall/lapi wrappers, safe fixture helpers, and libc/kernel headers selected by the source. Direct include dependencies include `stdint.h`, `config.h`, `lapi/syscalls.h`, `unistd.h`.

Risks and test signals: The main risk is environment sensitivity: kernel configuration, capabilities, filesystem support, libc/syscall variant differences, scheduler timing, or architecture ABI can turn intended assertions into skips or false failures. Test signals are emitted through `TCONF`.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/getdents/getdents.h -->
