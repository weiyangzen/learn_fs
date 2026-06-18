# sources/test-tools/liburing/src/arch/x86/lib.h

## sources/test-tools/liburing/src/arch/x86/lib.h

Purpose: x86 page-size helper.

Important APIs/functions: `get_page_size` returns constant 4096.

Control flow: no detection; always returns 4 KiB.

State and persistence: none.

Dependencies/integration: used by x86 liburing internals where 4 KiB page size is assumed for supported x86 Linux targets.

Risks: unsuitable for hypothetical x86 configurations with non-4K base pages. The simplicity avoids libc/procfs dependencies for nolibc.

Test signals: x86 and x86_64 CI builds and runtime memory mapping behavior.
