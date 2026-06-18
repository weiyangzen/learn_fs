# sources/test-tools/fio/lib/pattern.h

Purpose: public interface for fio pattern parsing and dynamic placeholder filling.

Important APIs/types: `MAX_PATTERN_SIZE`, `struct pattern_fmt_desc` with format string, reserved length, and paste callback; `struct pattern_fmt` with output offset and descriptor; parse, paste, copy, and compare function declarations.

Control flow/state: callers define supported placeholder descriptors, parse user pattern text into a pattern buffer plus `pattern_fmt` entries, and later paste runtime values into those entries before IO or verification.

Dependencies/integration: no includes; designed for use by option parsing and verify buffer code.

Risks/test signals: descriptor callbacks must tolerate partial lengths when a format extends beyond a shorter output buffer. Tests should validate descriptor count accounting and callback error propagation.
