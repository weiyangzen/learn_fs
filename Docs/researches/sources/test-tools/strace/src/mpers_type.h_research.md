<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/mpers_type.h -->
# sources/test-tools/strace/src/mpers_type.h

Purpose: abstracts mpers type includes and pointer representation for native and personality builds.
Important APIs/types/functions: `DEF_MPERS_TYPE`, `MPERS_PREFIX`, `MPERS_DEFS`, `mpers_ptr_t`, and guards for `IN_MPERS`, `MPERS_IS_m32`, and `MPERS_IS_mx32`.
Control flow: preprocessor maps parser declarations to generated headers during mpers generation and to `empty.h`/`native_defs.h` during normal builds. State and persistence behavior: declarations only.
Dependencies and integration points: all mpers-aware ioctl/socket decoders. Risks: wrong macro branch makes native builds include generated compat headers or vice versa. Test signals: mpers generation tests and native parser compilation.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/mpers_type.h -->
