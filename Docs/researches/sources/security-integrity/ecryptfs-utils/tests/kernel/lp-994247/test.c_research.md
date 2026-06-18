## sources/security-integrity/ecryptfs-utils/tests/kernel/lp-994247/test.c

Purpose: C regression test for Launchpad bug 994247 around `/dev/ecryptfs` misc device close ordering. It intentionally opens the eCryptfs misc device in a parent, forks a child inheriting the fd, closes the fd in the parent first, then signals the child to close its inherited descriptor.

Important APIs and functions: `main`, global `miscdev`, `sigusr1_handler`, `open`, `sigaction`, `fork`, `pause`, `kill`, `waitpid`, `close`. Control flow installs a `SIGUSR1` handler, forks, leaves the child paused, closes the parent fd, then asks the child to close and returns the child close status. State is only the process-shared inherited file descriptor value; persistence is none except kernel misc-device reference counting.

Dependencies and integration: Requires `/dev/ecryptfs` and a loaded eCryptfs kernel interface, normally driven by the surrounding kernel test harness. Risk is that failure modes can be kernel BUGs or hangs, not just nonzero exits. Test signal is binary: successful orderly close returns `0`; open, signal, wait, abnormal child exit, or child close failure returns `1`.
