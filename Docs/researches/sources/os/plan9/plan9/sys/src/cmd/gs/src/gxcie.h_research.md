# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gxcie.h

Internal CIE color implementation header. It declares CIE color-space procedures used by the color-space structures: initialization, restriction, installation, concretization/remapping, and concrete-space resolution for CIEA, CIEABC, CIEDEF, and CIEDEFG forms. It also exposes a CIE-to-XYZ imager-state helper used by pdfwrite.

The key macro is `CIE_CHECK_RENDERING`, which handles the no-rendering case by returning black and ensures joint CIE caches are completed before remapping. The header also declares remap finish implementations, common CIE GC descriptors, default initialization, common cache loading/completion, indirect installation, and construction of common CIE color-space storage. This is a declaration hub; implementations are in `gscie.c`, `gsciemap.c`, and `gscscie.c`.
