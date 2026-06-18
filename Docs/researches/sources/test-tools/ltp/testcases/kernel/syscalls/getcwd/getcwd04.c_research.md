<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/getcwd/getcwd04.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/getcwd/getcwd04.c

Purpose: Note: this test has already been in xfstests generic/028 test case, I just port it to LTP. Kernel commit '232d2d60aa5469bb097f55728f65146bd49c1d25' introduced a race condition that causes getcwd(2) to return "/" instead of correct path. 232d2d6 dcache: Translating dentry into pathname without taking rename_lock And these two kernel commits fixed the bug: ede4cebce16f5643c61aedd6d88d9070a1d23a68 prepend_path() needs to reinitialize dentry/vfsmount/mnt on restarts f6500801522c61782d4990fa1ad96154cb397cd4 f650080 __de

Important APIs/types/functions: includes `stdio.h`, `errno.h`, `fcntl.h`, `sys/types.h`, `unistd.h`, `tst_test.h`; touches `getcwd`; defines `do_child`, `sigproc`, `verify_getcwd`, `setup`; uses LTP safe helpers such as `SAFE_FORK`, `SAFE_GETCWD`, `SAFE_KILL`, `SAFE_RENAME`, `SAFE_SIGNAL`, `SAFE_TOUCH`, `SAFE_WAITPID`.

Control flow centers on `do_child`, `sigproc`, `verify_getcwd`, `setup`. The `struct tst_test` registration wires `.setup`, `.test_all`, `.needs_tmpdir`, `.forks_child` into the LTP runner.

State and persistence behavior: Runtime state is the process current working directory and path dentries; several tests mutate directories, symlinks, or renamed paths while checking returned buffers and errors.

Dependencies and integration points: Depends on the LTP test framework, Linux syscall/lapi wrappers, safe fixture helpers, and libc/kernel headers selected by the source. Direct include dependencies include `stdio.h`, `errno.h`, `fcntl.h`, `sys/types.h`, `unistd.h`, `tst_test.h`.

Risks and test signals: The main risk is environment sensitivity: kernel configuration, capabilities, filesystem support, libc/syscall variant differences, scheduler timing, or architecture ABI can turn intended assertions into skips or false failures. Test signals are emitted through `TFAIL`, `TPASS`.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/getcwd/getcwd04.c -->
