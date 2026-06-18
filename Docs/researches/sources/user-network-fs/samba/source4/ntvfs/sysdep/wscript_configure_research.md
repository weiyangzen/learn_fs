# sources/user-network-fs/samba/source4/ntvfs/sysdep/wscript_configure

Purpose: This configure fragment detects platform capabilities needed by NTVFS system-dependent notify and lease code.

Important APIs, types, and functions: It uses Python `sys.platform`, `conf.CHECK_HEADERS`, `conf.CONFIG_SET`, `conf.DEFINE`, and `conf.CHECK_DECLS`.

Control flow: It skips Linux inotify detection on SunOS/illumos even if headers exist because illumos inotify is not an exact Linux match. Otherwise it checks for `sys/inotify.h` and defines `HAVE_LINUX_INOTIFY` if present. It also checks declaration availability for `SA_SIGINFO`.

State and persistence behavior: It writes configure symbols that drive later build decisions. It does not affect runtime state directly.

Dependencies and integration points: The symbols are consumed by `sysdep/wscript_build`, `inotify.c`, and signal/lease code. The fragment depends on Waf configure context APIs.

Risks: Header presence is a weak proxy for full Linux-compatible inotify semantics. `SA_SIGINFO` detection affects signal-driven lease support and must match libc/kernel behavior.

Test signals: Configure tests on Linux, SunOS/illumos, and BSD-like hosts should confirm `HAVE_LINUX_INOTIFY` and `SA_SIGINFO` outcomes match expected backend build availability.
