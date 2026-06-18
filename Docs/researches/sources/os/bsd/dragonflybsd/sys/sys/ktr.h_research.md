# File Research: sources/os/bsd/dragonflybsd/sys/sys/ktr.h

Defines generic kernel trace-ring support. Core structures are `ktr_info`, `ktr_entry`, per-core `ktr_cpu_core`, and cache-aligned `ktr_cpu`. `KTR_INFO_MASTER`, `KTR_INFO`, `KTR_LOG`, and `KTR_COND_LOG` create typed, compile-time-checkable trace sites with sysctl-controlled masks.

Relevant to filesystem debugging because any subsystem can define trace classes and log compact event payloads into per-CPU buffers without full printf overhead.
