# sources/test-tools/syzkaller/pkg/report/testdata/linux/report/43

Purpose: Linux reporter parse fixture for syzkaller. It expects `kernel BUG in corrupted`, type `BUG`, corrupted `Y`, panicked `N`. The file is intentionally minimal and lacks enough stack context for a reliable function.

Important APIs, types, and functions: this exercises BUG detection and corruption marking in the Linux reporter. There are no meaningful crash frames beyond incidental architecture text.

Control flow: after headers, four body lines are parsed. The parser should detect a kernel BUG but mark the title function as corrupted rather than manufacturing a stack frame.

State and persistence behavior: `CORRUPTED: Y` is the key persistent expectation. Runtime parser state remains local to the test.

Dependencies, integration points, risks, and test signals: this guards partial-report behavior. Risks are false negatives for truncated BUG reports or false confidence with a clean title. Passing tests require BUG type, corrupted title, and no panic.
