<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/negated_errno.h -->
# sources/test-tools/strace/src/negated_errno.h

Purpose: common helper for detecting Linux negative errno return values with ABI-width awareness.
Important APIs/types/functions: `is_negated_errno`, `current_klongsize`, `MAX_ERRNO_VALUE`, and kernel-long truncation logic.
Control flow: truncates/comparses the supplied value to the current kernel long width and returns true for the conventional `-MAX_ERRNO_VALUE..-1` range. State and persistence behavior: pure helper.
Dependencies and integration points: architecture `get_error.c` files. Risks: wrong word-size handling misclassifies large successful returns as errors or vice versa. Test signals: boundary tests for `-1`, `-MAX_ERRNO_VALUE`, just outside range, and 32-bit compat returns.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/negated_errno.h -->
