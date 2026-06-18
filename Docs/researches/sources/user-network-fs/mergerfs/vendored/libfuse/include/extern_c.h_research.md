<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/libfuse/include/extern_c.h -->
# sources/user-network-fs/mergerfs/vendored/libfuse/include/extern_c.h

Purpose: This small compatibility header defines `EXTERN_C_BEGIN` and `EXTERN_C_END` so C ABI declarations can be shared by C and C++ translation units.

Important APIs: under C++ the macros expand to `extern "C" {` and `}`; under C they expand to nothing. Headers such as `fuse.h`, `fuse_common.h`, `fuse_lowlevel.h`, and `fuse_opt.h` use these wrappers around externally visible functions.

State and integration: there is no runtime state. Its only effect is linkage naming, which is critical because the vendored libfuse mixes C-compatible APIs with C++ implementation files.

Risks and test signals: mismatched macro placement can break linkage or nesting. A simple C and C++ compile/link test for public headers is sufficient.
<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/libfuse/include/extern_c.h -->
