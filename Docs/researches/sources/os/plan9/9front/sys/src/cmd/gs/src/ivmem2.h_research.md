# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/ivmem2.h

Declares VM control user-parameter procedures exported by `zvmem2.c` for use by `zusparam.c`. The two entry points are `set_vm_reclaim` and `set_vm_threshold`, both taking an interpreter context and a `long` value.

This header is a narrow bridge between user parameter handling and VM policy control.
