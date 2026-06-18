# sources/storage-engines/foundationdb/contrib/rapidjson/rapidjson/error/error.h

Purpose: This header defines RapidJSON parse error codes, the `ParseResult` value wrapper, and customization hooks for error-message character type and string literal conversion.

Important APIs and types: `ParseErrorCode` enumerates all reader/document parse failures, starting with `kParseErrorNone`. `ParseResult` stores a `ParseErrorCode` plus byte/code-unit offset and exposes `Code()`, `Offset()`, `operator bool`, `IsError()`, equality with codes or results, `Clear()`, and `Set()`. `GetParseErrorFunc` is a function pointer for locale-specific mappers such as `GetParseError_En`.

Control flow: Parsing code constructs or mutates `ParseResult` as it detects syntax or encoding failures. The boolean conversion returns success when `code_ == kParseErrorNone`; offsets are caller-supplied and meaningful only on error.

State and persistence behavior: `ParseResult` is a small in-memory value object. No filesystem or global state exists, but the macros `RAPIDJSON_ERROR_CHARTYPE` and `RAPIDJSON_ERROR_STRING` are compile-time ABI/configuration state that must remain consistent across translation units.

Dependencies and integration points: It includes `rapidjson.h` for namespace, size type, and diagnostic macros. Reader and document parse APIs return or expose these codes; `error/en.h` maps them to text.

Risks: Equality operators compare only `code_`, not `offset_`; tests or callers expecting offset-sensitive equality can be surprised. Adding, reordering, or renaming enum values affects diagnostics and localization tables. The macro customization surface can create mismatched string types if defined inconsistently.

Test signals: Cover success and error `ParseResult` construction, bool conversion, `Clear`/`Set`, equality ignoring offset, all enum values accepted by local message mappers, and customized error character builds.
