## sources/storage-engines/foundationdb/flow/actorcompiler/ParseTree.cs

Purpose: this C# file defines the actor-language abstract syntax tree shared by the parser and compiler. It is intentionally lightweight: most C++ expressions remain normalized strings, while actor-specific control constructs become typed nodes.

Important types and APIs: `VarDeclaration` stores type, name, initializer text, and whether initialization used constructor syntax. `Statement` is the base with `FirstSourceLine` and virtual `containsWait()`. Concrete statements include plain C++ code, state declarations, while/for/range-for/loop, break/continue, if/constexpr-if, return, wait, choose/when, try/catch, throw, and `CodeBlock`. `Actor` stores attributes, return type, name, enclosing class, parameters, template formals, body, source line, static/uncancellable/testcase/namespace/forward-declaration flags, and helpers `IsCancellable()`/`SetUncancellable()`.

Control flow: there is no execution flow beyond recursive `containsWait()` methods. The compiler relies on those methods to decide whether it can emit native C++ control flow or must split into continuations.

State and persistence behavior: parse-tree objects are in-memory only. Semantically, `StateDeclarationStatement` and actor parameters represent data that `ActorCompiler` will persist in generated state classes; the parse tree itself does not perform persistence.

Dependencies and integration points: consumed by both `ActorParser.cs` and `ActorCompiler.cs`. It models only enough C++ syntax for the actor compiler, leaving expression and plain statement text opaque.

Risks: adding a statement node requires matching parser production, `containsWait()` behavior, and compiler lowering. Incorrect `containsWait()` can make the compiler emit native loops around suspending code or over-split non-suspending code. The file contains a BOM-like character before `using System`, so tooling should keep encoding stable.

Test signals: successful parser/compiler tests across every statement class, especially nested `containsWait()` cases, are the main validation. Static compilation will also catch missing `CompileStatement` overloads for newly introduced statement classes.
