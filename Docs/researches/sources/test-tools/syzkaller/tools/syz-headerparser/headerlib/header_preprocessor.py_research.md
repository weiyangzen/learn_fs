# sources/test-tools/syzkaller/tools/syz-headerparser/headerlib/header_preprocessor.py

Purpose: this module preprocesses one or more C header files into a pycparser AST for the legacy header parser.

Important APIs and flow: `template` defines compatibility macros and typedefs to make Linux-like headers palatable to pycparser, then includes optional user-provided lines and copied header basenames. `HeaderFilePreprocessor.__init__` records filenames, logging, creates a temp directory/source/object file, copies headers, and runs GCC preprocessing. `_gcc_preprocess` executes `gcc -I. -E -P -c source.c > source.o`; `_get_ast` calls `pycparser.parse_file`; `get_ast` wraps parse errors in `HeaderFilePreprocessorException`.

State and persistence: creates a temporary directory and files but does not remove them in this code. The preprocessed output is stored as `source.o` in that temp dir.

Dependencies and integration: uses `gcc`, shell `cp`, pycparser, tempfile, and logging. Used by `StructWalker` when no AST is supplied.

Risks: command construction uses `shell=True` with joined filenames, so paths with spaces or shell metacharacters are unsafe. Temp files are leaked. It waits for process exit but does not inspect exit status. The compatibility macro set is partial.

Test signals: successful parsing of `test_headers` through `headerparser.py` or `StructWalker` is the practical signal.
