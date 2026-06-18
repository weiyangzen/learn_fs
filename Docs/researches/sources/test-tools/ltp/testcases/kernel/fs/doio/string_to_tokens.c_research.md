# sources/test-tools/ltp/testcases/kernel/fs/doio/string_to_tokens.c

Purpose: tokenizes a separator-delimited string into a caller-provided pointer array for legacy option parsing.

Important APIs/types/functions: `string_to_tokens`, `strtok`, `arg_string`, `arg_array`, `array_size`, and `separator`.

Control flow: rejects invalid output array, size, or separator with `-1`; calls `strtok(arg_string, separator)` for the first token; then continues until the array is full or no token remains. The output array is null-terminated when capacity permits, and the return value is the number of tokens stored/found within the bounded array walk.

State/persistence behavior: mutates `arg_string` by replacing separators with NUL bytes and uses `strtok`'s process-global scan state. It creates no filesystem state.

Dependencies/integration: used by `iogen` to split composite open-creation options such as `-O` argument forms.

Risks/test signals: not reentrant or thread-safe because of `strtok`. Extra tokens beyond `array_size - 1` are ignored. Callers must pass a writable string, not a string literal.
