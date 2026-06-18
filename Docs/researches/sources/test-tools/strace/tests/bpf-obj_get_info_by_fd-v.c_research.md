<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/bpf-obj_get_info_by_fd-v.c -->
## sources/test-tools/strace/tests/bpf-obj_get_info_by_fd-v.c

Purpose: Verbose map-info-only variant of `BPF_OBJ_GET_INFO_BY_FD`.

Important APIs/types/functions: Defines `VERBOSE 1` and includes `bpf-obj_get_info_by_fd.c`.

Control flow: Runs the common body without program loading but expands returned `bpf_map_info` fields symbolically.

State and persistence: Creates temporary BPF maps, serialized to reduce memlock contention.

Dependencies and integration: Uses map/prog xlat tables and BPF syscall support.

Risks: Map creation may fail due to permissions, kernel config, or memlock limits.

Test signals: Expected output includes detailed map info fields such as type, id, key/value sizes, flags, name, namespace ids, BTF fields, hash/map_extra when available.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/bpf-obj_get_info_by_fd-v.c -->
