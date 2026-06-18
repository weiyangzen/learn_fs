# sources/storage-engines/foundationdb/contrib/rapidjson/rapidjson/fwd.h

Purpose: This header centralizes forward declarations and default typedefs for RapidJSON's public types. It lets users and other headers refer to RapidJSON classes without pulling in full definitions.

Important APIs and types: It forward declares encodings, `Transcoder`, allocators, string streams, string buffers, file streams, memory streams, reader, writer, pretty writer, document/member/value types, pointer types, and schema types. Default typedefs include `StringStream`, `InsituStringStream`, `StringBuffer`, `MemoryBuffer`, `Reader`, `Value`, `Document`, `Pointer`, `SchemaDocument`, `IRemoteSchemaDocumentProvider`, and `SchemaValidator`.

Control flow: There is no executable flow. The header includes `rapidjson.h`, opens the configured namespace, declares templates/classes, and defines aliases wired to `UTF8<char>`, `CrtAllocator`, and `MemoryPoolAllocator<CrtAllocator>`.

State and persistence behavior: No state or persistence exists. The important behavior is compile-time dependency management and ABI consistency through shared typedef choices.

Dependencies and integration points: It is an integration surface across all RapidJSON modules. Code can include `fwd.h` in interfaces to avoid heavy dependencies on `document.h`, `reader.h`, `writer.h`, or `schema.h`.

Risks: Forward declarations must match the real template parameter lists exactly. The default typedefs couple callers to UTF-8 and default allocator choices. Any namespace customization must be visible consistently because these declarations live under `RAPIDJSON_NAMESPACE`.

Test signals: Compile-only tests should include `fwd.h` before and after full headers, instantiate all typedefs after including their definitions, and verify custom namespace builds.
