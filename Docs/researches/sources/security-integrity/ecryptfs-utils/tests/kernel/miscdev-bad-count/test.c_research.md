## sources/security-integrity/ecryptfs-utils/tests/kernel/miscdev-bad-count/test.c

Purpose: C probe for malformed count handling on `/dev/ecryptfs`. It writes a six-byte buffer to the misc device while passing an intentionally huge count (`1073741824`) and expects the kernel write path to reject the request.

Important APIs and functions: `main`, `open("/dev/ecryptfs", O_WRONLY)`, `write`, `close`. Control flow opens the misc device, writes using a small static buffer but a very large byte count, closes the descriptor, and returns `0` only if `write` failed. A successful write is considered a regression and returns `2`; open failure returns `1`.

State and persistence: No userspace persistent state; the test stresses kernel copy/count validation. Dependencies are the eCryptfs misc device and the wrapper that loads the module. Integration is direct with `miscdev-bad-count.sh`. Risks include undefined-looking userspace arguments intentionally used to validate kernel bounds; sanitizers or hardened libc wrappers may flag the test pattern, but kernel behavior is the target signal.
