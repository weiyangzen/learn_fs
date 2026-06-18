## sources/storage-engines/foundationdb/flow/actorcompiler/Properties/AssemblyInfo.cs

Purpose: this C# file supplies .NET assembly metadata for the actor compiler project.

Important APIs/types: assembly attributes define title/product as `actorcompiler`, description as `Compile Flow code to C++`, company as Apple Inc, COM visibility as false, typelib GUID, and assembly/file versions `1.0.0.0`.

Control flow: none; attributes are consumed by the compiler and runtime metadata readers.

State and persistence behavior: version and identity metadata are embedded in the compiled assembly. No runtime state is managed here.

Dependencies and integration points: uses `System.Reflection`, `System.Runtime.CompilerServices`, and `System.Runtime.InteropServices`. The metadata may affect packaging, file properties, and COM exposure.

Risks: copyright year and product metadata can drift from repository-wide conventions. Version numbers are fixed rather than generated, so package consumers cannot infer source revision from this file alone.

Test signals: build output inspection and assembly metadata checks are sufficient; functional actor compiler behavior is unaffected unless assembly metadata is used by packaging.
