<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/linux/x86_64/ioctls_arch2.h -->
# sources/test-tools/strace/src/linux/x86_64/ioctls_arch2.h

Purpose: x32 ioctl architecture table shim for personality 2.
Important APIs/types/functions: includes local `ioctls_arch0.h`, reusing native x86_64 ioctl encodings.
Control flow: no executable logic. State and persistence behavior: build-time alias.
Dependencies and integration points: ioctl decoder under x32 personality. Risks: x32-specific ioctl differences would be missed. Test signals: x32 ioctl decoding tests for pointer-sized structures.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/linux/x86_64/ioctls_arch2.h -->
