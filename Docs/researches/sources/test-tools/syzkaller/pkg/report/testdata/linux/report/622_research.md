# sources/test-tools/syzkaller/pkg/report/testdata/linux/report/622

## Purpose
This fixture covers a refcount warning in `memfd_secret`, with alternates for syscall wrapper names.

## Important APIs, types, and functions
Key symbols include `refcount_warn_saturate`, `__se_sys_memfd_secret`, `do_syscall_64`, and `entry_SYSCALL_64_after_hwframe`.

## Control flow
A userspace call to the memfd secret syscall triggers `refcount_t: addition on 0; use-after-free`, then emits a standard warning stack.

## State and persistence behavior
The file persists a refcount warning without a panic. The expected aliases account for syscall wrapper variation.

## Dependencies and integration points
It tests the report parser's refcount warning type, syscall wrapper normalization, and memfd-secret naming.

## Risks and test signals
The parser must classify the type as `REFCOUNT_WARNING` and prefer `WARNING: refcount bug in memfd_secret` over the generic refcount helper.
