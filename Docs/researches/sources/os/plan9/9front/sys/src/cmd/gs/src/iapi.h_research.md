# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/iapi.h

Declares the public Ghostscript interpreter API for DLL/static embedding.

Key points:
- Defines platform-specific export and calling-convention macros for Windows, OS/2, Mac, and generic builds.
- Declares `gsapi_revision_t`.
- Warns prominently that only one Ghostscript instance is supported.
- Declares instance lifecycle, stdio callbacks, poll callback, display callback, interpreter initialization, string/file execution, exit, and visual tracer APIs.
- Documents callback contracts and return-code behavior for initialization and run functions.
- Provides function pointer typedefs for dynamic loading.

Research notes:
- This is a public ABI header, so calling convention correctness is emphasized.
- The comments encode important lifecycle rules: call `gsapi_exit` after initialization and before deleting an instance.
