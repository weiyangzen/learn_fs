# sources/security-integrity/selinux/libselinux/src/avc_sidtab.h

Purpose: This header declares the SID table data structures and operations used by the AVC implementation to map context strings to process-local security IDs.

Important APIs/types/functions: `struct sidtab_node` embeds `struct security_id` and a next pointer. `struct sidtab` owns a bucket array and entry count. Constants define a 7-bit, 128-bucket table. Function declarations cover init, lookup, context-to-SID insertion, stats, and destroy.

Control flow: there is no executable logic here, but the structure layout is directly consumed by `avc_sidtab.c` and by `avc.c` through opaque `security_id_t` pointers.

State and persistence: the header defines the shape of process-local persisted SID table state. Entries are not kernel SIDs; they are stable in-memory handles.

Dependencies and integration: includes public `selinux/selinux.h` and `selinux/avc.h`, so it is tied to libselinux public SID types.

Risks and test signals: ABI risk is internal, but pointer stability and bucket sizing affect AVC cache behavior. Tests should verify that consumers never treat the integer `id` as a kernel-visible SID.
