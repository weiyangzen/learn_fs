# sources/test-tools/strace/src/resource.c

Purpose: Decodes resource-limit, rusage, and priority syscalls.

Important APIs/types/functions: `getrlimit`, `setrlimit`, `prlimit64`, `getrusage`, Alpha `osf_getrusage`, `getpriority`, `setpriority`; helpers `print_rlim64_t`, `print_rlim32_t`, `decode_rlimit`, and `priority_print_who`.

Control flow: limit syscalls print resource on entry and output structures on exit for getters. `decode_rlimit` chooses 32-bit vs 64-bit layout by kernel long size/personality. `prlimit64` prints new limit on entry and old limit on exit. Priority syscalls print `who` as pid/process group depending on `which`.

State and persistence: stateless; output phase decides old-limit/rusage fetches.

Dependencies/integration: `<sys/resource.h>`, resources/usagewho/priorities xlat, rusage printer, pid helpers, and xlat verbosity for infinity and `*1024` formatting.

Risks: rlim_t width differs on i386/x32/64-bit. Static buffers in rlim helper are transient. Alpha has separate rusage ABI. Return-value decoding for `getpriority` is handled elsewhere, so argument decoder must not confuse negative priorities with errors.

Test signals: get/set/prlimit64 on 32- and 64-bit personalities, infinity values, multiples of 1024, getrusage abbrev/full, priority process/pgrp/user cases.
