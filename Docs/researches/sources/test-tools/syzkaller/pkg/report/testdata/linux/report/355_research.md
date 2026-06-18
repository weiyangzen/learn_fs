<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/355 -->
# sources/test-tools/syzkaller/pkg/report/testdata/linux/report/355

## Purpose
This fixture verifies Trusty panic normalization for app start failures with dynamic numbers. The expected title is `trusty: panic: failed(-NUM) to start app NUM`.

## Important APIs, Types, And Functions
The raw log includes Trusty page-table allocation failures, `failed(-5) to allocate data segment`, `failed(-5) to load address map`, and `panic ... failed(-5) to start app 6`, followed by the Linux Trusty warning wrapper and arm64 workqueue stack.

## Control Flow
The parser must extract the Trusty panic root and normalize dynamic error/app values to `NUM`. It then handles the Linux panic-on-warn wrapper as panicked state, not as the title.

## State And Persistence
Persistent state is the normalized title, type `DoS`, and panicked flag. Runtime state includes secure-world loader memory allocation failure and Trusty halt reason.

## Dependencies And Integration Points
It depends on Trusty panic parsing, numeric normalization, multiline prefix cleanup, and panic-on-warn detection.

## Risks
The app UUID fragment and numeric error codes can produce unstable titles if normalization changes.

## Test Signals
Expected parse title is exactly `trusty: panic: failed(-NUM) to start app NUM`, type `DoS`, panicked.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/355 -->
