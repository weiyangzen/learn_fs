## sources/storage-engines/foundationdb/flow/actorcompiler_py/parse_tree.py

Purpose: this Python file defines the dataclass AST used by the Python actor compiler port. It mirrors `ParseTree.cs` while using Python naming and type annotations.

Important types and APIs: `VarDeclaration`, abstract `Statement`, `CodeBlock`, `PlainOldCodeStatement`, `StateDeclarationStatement`, `WhileStatement`, `ForStatement`, `RangeForStatement`, `LoopStatement`, `BreakStatement`, `ContinueStatement`, `IfStatement`, `ReturnStatement`, `WaitStatement`, `ChooseStatement`, `WhenStatement`, `TryStatement` with nested `Catch`, `ThrowStatement`, and `Actor`. Each statement implements `contains_wait()`; `Actor` implements `is_cancellable()` and `set_uncancellable()`.

Control flow: no runtime actor control flow is executed. Recursive `contains_wait()` is the key behavioral API used by `actor_compiler.py` to choose native C++ emission or continuation splitting.

State and persistence behavior: dataclasses are transient parse results. Actor parameters and state declarations are later converted into generated C++ state fields, but this file does not persist anything itself.

Dependencies and integration points: depends on `abc`, `dataclasses`, and typing primitives. Consumed by `actor_parser.py` and `actor_compiler.py`.

Risks: default factories avoid shared mutable defaults for statement bodies and lists. Any new statement class must implement `contains_wait()` and be added to parser/compiler dispatch. Because `Statement.contains_wait` is abstract, accidental instantiation of base statements is prevented.

Test signals: parser/compiler tests indirectly validate all dataclasses. Direct unit tests can verify `contains_wait()` propagation through nested blocks, if/else, loops, choose/when, and try/catch.
