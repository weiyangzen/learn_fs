# File Research: sources/os/bsd/netbsd-src/lib/libedit/TEST/test_filecompletion.c

This test verifies libedit filename completion escaping behavior.

Test model:
- Defines many `test_input` cases with:
  - wide-character user-typed command text,
  - expected input seen by the completion function,
  - one or two generated completion matches,
  - expected escaped output in the edit buffer.
- Cases cover angle brackets, backslashes, braces, dollars, equals, newlines, spaces, quotes, parentheses, pipes, tabs, backticks, `@`, semicolons, ampersands, cursor-at-quote/backslash behavior, and multiple-match common-prefix completion.

Key functions:
- `mycomplet_func()` returns hardcoded matches based on the current completion text.
- `main()` initializes `EditLine`, writes each test input directly into `el->el_line`, calls `fn_complete()`, prints the expected/generated values, and asserts that the edited buffer matches.

Integration:
- Includes internal headers `filecomplete.h` and `el.h`, so it tests internals rather than only public API.
- Uses `FN_QUOTE_MATCH` behavior through `fn_complete()` when no attempted completion function is supplied.

Risks and notes:
- The test mutates `el->el_line` directly, bypassing normal editing setup.
- It allocates a fixed 64-wide-character buffer and uses a pointer limit larger than 64 wchar slots because it adds `64 * sizeof(*buffer)` to a `wchar_t *`; the test data remains small enough that this does not affect intended coverage.
