# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/sbcp.h

Declares BCP/TBCP stream templates and decode state. Encoding has no custom state, while decode state includes callback pointers for interrupt/status requests and dynamic fields for escape handling and tagged copy behavior.

Dependencies are Ghostscript stream common definitions and `strimpl.h` when templates are referenced.

This is printer protocol stream plumbing, not filesystem code.
