# File Research: sources/os/plan9/9front/sys/src/cmd/cpp/test/edges.in

Cpp edge-case test input focused on macro expansion semantics. It is not C code meant for compilation; it exercises preprocessor output behavior.

Important coverage:
- `##` with empty left/right arguments.
- Nested token pasting and expansion ordering.
- Variadic macros with and without `__VA_ARGS__`.
- Comma expansion inside macro arguments.
- C standard complex macro examples involving self-reference/hidesets.
- Empty argument stringification and token pasting.
