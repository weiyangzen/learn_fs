<!-- BEGIN_FILE_RESEARCH: sources/test-tools/filebench/cvars/cvar_tokens.h -->
# `sources/test-tools/filebench/cvars/cvar_tokens.h`

Purpose: Token utility interface for CVAR parameter parsing.

Important types/macros: `DEFAULT_PARAMETER_DELIMITER` is `;`, `DEFAULT_KEY_VALUE_DELIMITER` is `:`, and `cvar_token_t` stores `key`, optional `value`, `used`, and `next`.

Control flow: declares tokenizer, lookup, unused-token scan, and free functions; no runtime implementation here.

State and persistence: token state is a mutable linked list used during handle allocation. `used` lets modules detect unknown parameters after consuming known keys.

Dependencies and integration: included by all distribution plugins and implemented in `cvar_tokens.c`.

Risks: API exposes mutable linked-list internals, so callers can corrupt list invariants. Delimiters are single chars and there is no escaping/quoting support.

Test signals: compile all modules against the header and unit-test token list behavior through the public functions.
<!-- END_FILE_RESEARCH: sources/test-tools/filebench/cvars/cvar_tokens.h -->
