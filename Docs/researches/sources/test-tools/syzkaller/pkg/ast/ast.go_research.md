# sources/test-tools/syzkaller/pkg/ast/ast.go

## Purpose
Defines the AST model for syzkaller syscall description (`sys`) files.

## Important APIs, Types, and Functions
Core types are `Pos`, `Description`, `Node`, `Flags`, and `FlagValue`. Top-level nodes include `NewLine`, `Comment`, `Meta`, `Include`, `Incdir`, `Define`, `Resource`, `Call`, `Struct`, `IntFlags`, `StrFlags`, and `TypeDef`. Expression/value nodes include `Ident`, `String`, `Int`, `BinaryExpression`, `Type`, and `Field` with format enums and operators.

## Control Flow
There is no parser logic here; each node implements `Info` and some flag nodes implement mutation/accessor methods. `Clone` and `walk` contracts are declared through the `Node` interface and implemented in other files.

## State and Persistence Behavior
AST nodes are in-memory mutable structs representing parsed source positions and declarations. Persistence happens through formatting elsewhere.

## Dependencies and Integration Points
Used by parser, formatter, clone/filter/walk utilities, compiler stages, and syzlang tooling.

## Risks and Test Signals
Risks include nil subnodes, format-field invariants where only one variant should be set, and stable `Info` type strings. Parser round-trip tests exercise the model broadly.
