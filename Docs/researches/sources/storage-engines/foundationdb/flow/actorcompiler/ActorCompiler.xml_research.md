## sources/storage-engines/foundationdb/flow/actorcompiler/ActorCompiler.xml

Purpose: this Visual Studio/MSBuild rule schema declares the Flow Actor Compiler as a project item/tool. It lets `.actor.cpp` files be recognized by the IDE/build property system as `ActorCompiler` content.

Important types and APIs: the XML defines a `Rule` named `ActorCompiler` with `PageTemplate="tool"` and item type `ActorCompiler`. It exposes `EnableCompile` as a boolean option, `ActorCompilerOptions` as tool-specific options, and `AdditionalOptions` as command-line options passed onward to the C++ compiler handling generated output. It also maps `.actor.cpp` to the `ActorCompiler` content type and declares a separate `Dependency` item/content type.

Control flow: there is no executable control flow; MSBuild/Visual Studio loads this rule metadata to show property pages and bind file extensions to item types.

State and persistence behavior: properties persist in the project file through the `DataSource` configured with `Persistence="ProjectFile"` and `ItemType="ActorCompiler"`. The file itself does not store runtime state.

Dependencies and integration points: the schema uses `Microsoft.Build.Framework.XamlTypes`, `Microsoft.VisualStudio.Project.Contracts.Implementation`, and `mscorlib` XML namespaces. It integrates the C# actor compiler into Visual Studio project tooling rather than the Flow runtime.

Risks: build behavior can drift if property names no longer match project targets/tasks. The schema is IDE/build-system metadata, so errors may appear as missing property pages or incorrect `.actor.cpp` handling rather than compiler failures.

Test signals: validation is project load/build behavior in Visual Studio/MSBuild, correct recognition of `.actor.cpp`, and command-line construction that includes actor compiler and C++ additional options.
