# sources/test-tools/ltp/testcases/kernel/syscalls/remap_file_pages/remap_file_pages02.c

## Purpose

`sources/test-tools/ltp/testcases/kernel/syscalls/remap_file_pages/remap_file_pages02.c` is a 158-line LTP source file in the `remap_file_pages` syscall test area. remap_file_pages virtual-memory coverage for file-backed mappings, page remapping, and invalid parameter/error behavior. Source description: DESCRIPTION The remap_file_pages() system call is used to create a non-linear mapping, that is, a mapping in which the pages of the file are mapped into a non-sequential order in memory.  The advantage of using remap_file_pages() over using repeated calls to mmap(2) is that the former  approach  does  not require the kernel to create additional VMA (Virtual Memory Area) data structures. Runs remap_file_pages with wrong values and see if got the expected error

## Important APIs, Types, and Functions

called APIs/macros: `remap_file_pages`, `mmap`, `SAFE_CLOSE`, `SAFE_FTRUNCATE`, `SAFE_MMAP`, `SAFE_MUNMAP`, `SAFE_OPEN`, `TEST`; local functions: `setup01`, `setup02`, `setup03`, `setup04`, `run`, `setup`, `cleanup`; struct/table types referenced: `struct tcase`, `struct tst_test`; important macros/constants: `_GNU_SOURCE`, `WINDOW_START`.

## Control Flow

Function-level flow is organized around `setup01`, `setup02`, `setup03`, `setup04`, `run`, `setup`, `cleanup`. The LTP harness calls setup hooks to create files, mounts, sockets, keys, signal handlers, or descriptors, then dispatches either a per-case `.test` callback or a `.test_all` callback, and finally runs cleanup hooks to close descriptors and remove temporary state. Case tables drive repeated checks over expected success/error outcomes, descriptors, flags, quotas, signals, or policies.

## State and Persistence Behavior

State is temporary filesystem state created under the LTP scratch directory or mounted test device: files, directories, symlinks, xattrs, descriptors, and pathnames are mutated and then removed.

## Dependencies and Integration Points

Direct includes: `<sys/mman.h>`, `<sys/types.h>`, `<sys/stat.h>`, `<fcntl.h>`, `<stdio.h>`, `<unistd.h>`, `<errno.h>`, `<sys/syscall.h>`, `<linux/unistd.h>`, `"tst_test.h"`, `"lapi/syscalls.h"`. Uses the modern LTP `tst_test` harness for setup, cleanup, variants, filesystem requirements, and result reporting. Designated initializer fields seen include `.tcnt`, `.test`, `.cleanup`, `.setup`, `.needs_tmpdir`. Depends on LTP `lapi` wrappers for direct syscall numbers, compatibility structures, or missing libc declarations.

## Risks and Edge Cases

The main risk is errno drift or unsupported syscall behavior across architectures, kernel versions, and libc wrapper availability. Explicit errno expectations include `EINVAL`.

## Test Signals

TPASS/TST_EXP_PASS success reports; TFAIL/TST_EXP_FAIL errno or invariant checks; notable reported messages include `remap_file_pages(2) %s expected %s got`.
