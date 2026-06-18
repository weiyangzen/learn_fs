# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gsicc.c

## Role

`gsicc.c` implements Ghostscript ICCBased color spaces: color-space descriptors, color restriction/concretization, ICC profile loading through icclib, Ghostscript-stream wrapping for icclib I/O, reference-count adjustment, finalization of foreign ICC memory, construction, installation, and serialization.

This is color-management infrastructure, not filesystem code.

## Main Interfaces

- Public/external functions: `gx_load_icc_profile`, `gs_cspace_build_CIEICC`, `gx_increment_cspace_count`.
- Color-space methods: `gx_num_components_CIEICC`, `gx_alt_space_CIEICC`, `gx_init_CIEICC`, `gx_restrict_CIEICC`, `gx_concrete_space_CIEICC`, `gx_concretize_CIEICC`, `gx_adjust_cspace_CIEICC`, `gx_install_CIEICC`, `gx_serialize_CIEICC`.
- icclib bridge: `gx_wrap_icc_stream`, `icmFileGs_seek`, `icmFileGs_read`, `icmFileGs_write`, `icmFileGs_flush`, `icmFileGs_delete`.

## Core Behavior

- ICCBased color spaces either use the loaded ICC profile or fall back to the inline alternate color space if no profile is loaded.
- Profile loading validates the stream identity, profile class, profile connection space, and component count, then creates an icclib lookup object.
- Concretization verifies the underlying stream has not been closed/reused, clamps input to declared ranges, massages Lab input/output as needed, runs the ICC lookup, converts PCS Lab to XYZ when necessary, and finishes through the CIE remap cache.
- The wrapper `icmFileGs` adapts Ghostscript streams to icclib's file API and is allocated with C `calloc`; finalization calls icclib destructors and frees the wrapper through its `del` method.
- Serialization writes common CIE state, component count/ranges, the raw ICC stream bytes, and the Lab/XYZ PCS flag.

## Notable Risks

- The file intentionally uses “foreign” non-GC memory for icclib objects; finalization must run to avoid leaks.
- The stream pointer held by icclib is lazily refreshed before lookup, and `file_id` checks are used to detect closed/reused streams.
- `icmFileGs_read`/`write` return `size_t` but propagate negative stream status values through the return expression, which is awkward for a size-returning API.
- Several comments note color-management assumptions and potential correctness limits around ICC rendering intent.
- Serialization depends on seeking and measuring `picc->instrp`; unsupported stream behavior returns `unregistered`.
