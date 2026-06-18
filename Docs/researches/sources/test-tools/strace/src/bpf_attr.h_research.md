<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/bpf_attr.h -->
## sources/test-tools/strace/src/bpf_attr.h

Purpose: Provides strace-local, command-specific mirrors of `union bpf_attr` and BPF object info structs. The file lets `bpf.c` decode kernel BPF UAPI across multiple kernel generations without relying entirely on the build host headers.

Important APIs and types: Defines structs such as `BPF_MAP_CREATE_struct`, `BPF_PROG_LOAD_struct`, `BPF_OBJ_PIN_struct`, `BPF_PROG_ATTACH_struct`, `BPF_PROG_TEST_RUN_struct`, `BPF_OBJ_GET_INFO_BY_FD_struct`, `BPF_PROG_QUERY_struct`, `BPF_BTF_LOAD_struct`, `BPF_LINK_CREATE_struct`, `BPF_TOKEN_CREATE_struct`, `BPF_PROG_STREAM_READ_BY_FD_struct`, and `BPF_PROG_ASSOC_STRUCT_OPS_struct`. It also defines `bpf_map_info_struct`, `bpf_prog_info_struct`, expected size macros, and aliases for commands sharing layouts.

Control flow: Header-only data contract; no executable flow. `bpf.c` uses each `*_struct_size` macro as the maximum known decode length, then gates optional fields with `offsetof` checks.

State and persistence: No runtime state. The meaningful persistence is ABI shape: fixed field order, `ATTRIBUTE_ALIGNED(8)` on all `uint64_t` fields, and expected size constants that should catch unexpected build-time layout changes.

Dependencies and integration: Included by `bpf.c` after kernel BPF headers. Relies on basic integer types, `ATTRIBUTE_ALIGNED`, and `offsetofend` from common strace headers. It intentionally documents kernel UAPI breakage with `skip check` comments where layout quirks are known.

Risks: Any mismatch with current kernel UAPI can corrupt decode output. New fields require both this header and `bpf.c` command decoders to be updated. Union members in `BPF_LINK_CREATE_struct` are especially fragile because the decoder guesses active members from attach type and flags.

Test signals: Build-time size checks and bpf syscall tests should validate every `expected_*_size`. Runtime tests should cover old attr lengths, new trailing fields, and each alias macro such as map batch operations or id iteration commands.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/bpf_attr.h -->
