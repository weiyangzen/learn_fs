# sources/test-tools/syzkaller/pkg/serializer/serializer.go

## Purpose

`serializer.go` writes a compact Go-syntax representation of values for syzkaller diagnostics and generated data, improving on `fmt %#v` for pointer-heavy structs and default-valued fields.

## Important APIs, Types, And Control Flow

`Write(io.Writer, any)` and `WriteString(any)` are public entry points. The private `writer` recursively handles pointers, interfaces, slices, structs, booleans, signed/unsigned integers, strings, and nil funcs. Structs omit default or unsettable fields and then switch to named-field syntax; slices of pointer/interface/struct elements are rendered multiline. Interfaces wrapping named primitive types are emitted as `Type(value)` so deserialization preserves the user type. `isDefaultValue` recursively recognizes zero values.

## State, Dependencies, Integration, Risks, And Test Signals

The serializer is stateless beyond the destination writer and reflection stack. Dependencies are `reflect`, `strings`, `fmt`, and `io`. It does not support maps, channels, non-nil functions, or pointers to non-structs, and it panics for unsupported cases. `reflect.Value.CanSet` is used to skip unexported/default fields, which makes output sensitive to addressability. `serializer_test.go` covers nested structs, pointers, slices, escaped strings, named primitive interface values, nils, and nil funcs.
