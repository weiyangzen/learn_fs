# sources/test-tools/strace/maint/gen/symbols.h

Purpose: public interface for generator symbol registration and type resolution.

Important APIs/types/functions: prototypes `resolve_type`, `symbol_add`, and `symbol_get`; includes `ast.h`.

Control flow: not executable; consumers call these functions during parsing and AST type interning.

State and persistence behavior: documents return contracts but not the underlying global symbol table.

Dependencies and integration points: included by `parse.y`, `ast.c`, `preprocess.c`, and `codegen.c`.

Risks: sparse documentation leaves ownership and thread-safety implicit. Header guard closing comment has a compact `//SYMBOLS_H` style but no functional issue.

Test signals: generator builds and duplicate/type-error parser tests exercise this interface.
