<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/log/test_display.c -->
# sources/user-network-fs/nfs-ganesha/src/log/test_display.c

## Purpose
This is a small display-buffer exerciser for the logging/display utility layer. It manually drives `display_printf()`, `display_reset_buffer()`, and `display_opaque_value()` against buffers of different sizes to observe truncation, concatenation, and opaque-byte formatting behavior.

## Important APIs, Types, and Functions
`show_display_buffer()` prints a comment, buffer size, current string length, and buffer contents. `main()` constructs three `struct display_buffer` instances backed by local arrays of 10, 200, and 14 bytes. It calls `display_printf()` repeatedly with strings and integers, resets buffers, and calls `display_opaque_value()` on printable and non-printable byte sequences.

The opaque inputs include a printable string, short binary strings with embedded NUL bytes, and data ending around newline/NUL combinations. Some calls intentionally pass `strlen(opaque3) + 3` to include bytes after the first NUL.

## Control Flow
Execution is linear. Each scenario writes to a display buffer, calls `show_display_buffer()` with a label, then resets before the next scenario. The early tests fill a small buffer with repeated `foo` strings and integer formatting to exercise boundary behavior. Later tests compare opaque formatting in a small buffer, large buffer, and 14-byte buffer.

## State and Persistence Behavior
All state is stack-local. Output is written to stdout for manual or script-based comparison. The test does not persist artifacts by itself and does not assert internally.

## Dependencies and Integration Points
The file depends on `display.h` and the display-buffer implementation elsewhere in the log/support code. It integrates with old log tests by producing deterministic stdout that a harness can inspect. It does not include `log_functions.c`, but it validates lower-level formatting helpers used by logging.

## Risks and Edge Cases
Because the test only prints observations, failures require an external golden-output comparison or manual inspection. Embedded NUL strings mean `strlen()` intentionally stops early in some cases; the one `strlen() + 3` case is designed to include hidden bytes but is easy to misunderstand. The `%z` length format in `show_display_buffer()` assumes the local platform/compiler accepts that length modifier as used here.

## Test Signals
Useful signals are stable stdout lines showing expected truncation and NUL-termination for small buffers, correct reset behavior after repeated calls, integer formatting consistency between small and large buffers, and readable/escaped output for opaque binary values.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/log/test_display.c -->
