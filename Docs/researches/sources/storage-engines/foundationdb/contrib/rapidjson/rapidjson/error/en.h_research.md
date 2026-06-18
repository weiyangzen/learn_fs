# sources/storage-engines/foundationdb/contrib/rapidjson/rapidjson/error/en.h

Purpose: This header provides RapidJSON's default English parse-error message mapper. It translates `ParseErrorCode` enum values from `error.h` into human-readable strings for diagnostics.

Important APIs and types: The single public API is `GetParseError_En(ParseErrorCode)`, returning `const RAPIDJSON_ERROR_CHARTYPE*`. It covers every parse error declared in `error.h`, including document, value, object, array, string, number, termination, and unspecific syntax errors. Messages are wrapped in `RAPIDJSON_ERROR_STRING()` so users can redefine error character handling.

Control flow: The function is an inline `switch` over `ParseErrorCode`. Known codes return fixed string literals; the default branch returns "Unknown error." This switch-based mapping is intentionally safer when enum values are extended because new cases remain visible in compiler diagnostics when warnings are enabled.

State and persistence behavior: There is no runtime state or persistence. Returned pointers refer to static string literals in the translation unit after macro expansion.

Dependencies and integration points: It includes `error.h` and is commonly used with `ParseResult::Code()`, `GenericReader::GetParseErrorCode()`, and `GenericDocument::GetParseError()`. Applications can copy this file to localize messages.

Risks: Message text is part of user-facing diagnostics, so changing strings can break tests that assert exact output. Locale customization depends on consistent `RAPIDJSON_ERROR_CHARTYPE` and `RAPIDJSON_ERROR_STRING` definitions across all included RapidJSON headers.

Test signals: Verify every `ParseErrorCode` maps to the expected English message, unknown numeric codes map to the fallback, and custom `RAPIDJSON_ERROR_CHARTYPE`/`RAPIDJSON_ERROR_STRING` builds compile.
