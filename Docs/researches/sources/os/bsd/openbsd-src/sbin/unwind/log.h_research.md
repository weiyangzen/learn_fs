# File Research: sources/os/bsd/openbsd-src/sbin/unwind/log.h

`log.h` declares unwind's logging API and maps the generic names `log_init`, `log_warn`, and `log_info` to unwind-prefixed implementations to avoid conflicts with libunbound's logging symbols.

It exposes debug/verbose getters and setters, process-name initialization, warn/info/debug/logit/vlog functions, and `__dead` fatal exits. The variadic functions carry printf-format attributes, making compile-time format checking available to callers.
