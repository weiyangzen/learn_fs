# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/ipacked.h

Ghostscript packed-array encoding header. It documents and defines the compact 2-byte `ref_packed` representation used alongside full-size refs in packed arrays.

Key contents:
- Documents the bit layout for full refs, executable operators, packed integers, literal names, and executable names.
- Defines `packed_type` values: `pt_full_ref`, `pt_executable_operator`, `pt_integer`, unused tags, `pt_literal_name`, and `pt_executable_name`.
- Defines packed/ref alignment helpers: `packed_per_ref` and `align_packed_per_ref`.
- Defines tag and mask macros: `pt_tag`, `packed_value_mask`, `packed_max_value`.
- Defines packed detection helpers: `r_is_packed`, `r_packed_is_name`, and `r_packed_is_exec_name`.
- Defines packed name extraction and maximum index.
- Defines packed integer min/max values and mask.
- Defines packed mark-bit helpers for GC.
- Defines `packed_next` to advance through mixed packed/full refs.
- Defines `ref_array_packing` as the current setpacking/currentpacking state stored in `i_ctx_p`.

Notable dependencies:
- Requires `ref`, `ref_packed`, and architecture alignment macros supplied by surrounding interpreter headers.

Research notes:
- `interp.c`, `zpacked.c`, and GC compaction code know more about the packed representation than this header alone abstracts.
- The file emphasizes that mixed arrays must preserve full-ref alignment on architectures that fault on unaligned access.
- Packed names can only encode indices up to 12 bits; larger name indices require full refs.
