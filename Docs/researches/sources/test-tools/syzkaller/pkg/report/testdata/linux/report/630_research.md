# sources/test-tools/syzkaller/pkg/report/testdata/linux/report/630

## Purpose
This fixture validates a stack guard hit attributed to `tls_setsockopt`.

## Important APIs, types, and functions
Key symbols include `__sanitizer_cov_trace_const_cmp4`, TLS setsockopt paths, stack-unwind frames, and syscall/socket option handling. The expected alternate is `stack-overflow in tls_setsockopt`.

## Control flow
The log shows at least two guard-page hits while a TLS socket option path recurses or overuses stack. Instrumentation and coverage frames appear at the top, so the parser must recover the semantic entry point.

## State and persistence behavior
The fixture persists guard-page addresses, task metadata, register state, and expected title metadata.

## Dependencies and integration points
It tests stack-overflow parsing in networking TLS code and filtering of sanitizer coverage frames.

## Risks and test signals
The parser must not title the crash as a sanitizer coverage helper. The expected title is `BUG: stack guard page was hit in tls_setsockopt`.
