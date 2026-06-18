# sources/storage-engines/sqlite/tool/lempar.c

## Purpose
`lempar.c` is the Lemon parser driver template. `lemon.c` copies this file to generated parser output and replaces each `%%` separator with generated includes, token definitions, control macros, parse tables, fallback tables, symbolic names, destructor cases, reduce actions, and user-supplied hooks. Any `Parse` identifier prefix is rewritten to the grammar `%name` value.

## Important APIs, Types, and Functions
- Generated parser state types: `struct yyStackEntry` stores state/action number, major token, and semantic minor value; `struct yyParser` stores the stack, top pointer, optional high-water mark, error recovery counter, `%extra_argument`, and `%extra_context`.
- Public parser API in generated output: `ParseTrace()` in debug builds, `ParseInit()`, `ParseAlloc()`, `ParseFinalize()`, `ParseFree()`, optional `ParseStackPeak()`, optional `ParseCoverage()`, main `Parse()`, and `ParseFallback()`.
- Core runtime helpers: `yyGrowStack`, `yy_destructor`, `yy_pop_parser_stack`, `yy_find_shift_action`, `yy_find_reduce_action`, `yyStackOverflow`, `yyTraceShift`, `yy_shift`, `yy_reduce`, `yy_parse_failed`, `yy_syntax_error`, and `yy_accept`.
- Generated tables/macros: `yy_action`, `yy_lookahead`, `yy_shift_ofst`, `yy_reduce_ofst`, `yy_default`, `yyFallback`, `yyTokenName`, `yyRuleName`, `yyRuleInfoLhs`, `yyRuleInfoNRhs`, `YYCODETYPE`, `YYACTIONTYPE`, `YYMINORTYPE`, `YYSTACKDEPTH`, `YYERRORSYMBOL`, and action-range constants.

## Control Flow
1. A caller allocates or provides a parser, initializes it with state 0 on the stack, then repeatedly calls `Parse(parser, major, minor, extra_arg)` with tokens. Token 0 is end-of-input.
2. `Parse()` starts from the current top stack state and calls `yy_find_shift_action()` for terminal lookahead. That routine consults offset/action/lookahead tables, then fallback and wildcard handling if the direct table entry misses.
3. If the action is reduce, `Parse()` calls `yy_reduce()`, which runs generated reduce code, computes the LHS nonterminal, finds the goto action with `yy_find_reduce_action()`, pops RHS entries, pushes the LHS, and loops for more reductions.
4. If the action is shift or shift-reduce, `yy_shift()` pushes the token and semantic value, grows the stack if configured, translates pending shift-reduce states into reduce action numbers, and returns to the caller.
5. If the action is accept, `Parse()` pops the start marker, calls `yy_accept()`, and returns.
6. If the action is syntax error, behavior depends on generated macros: with `YYERRORSYMBOL`, it calls syntax-error code, pops until the error token can shift, shifts error, and suppresses repeated errors for three successful shifts; with `YYNOERRORRECOVERY`, it reports and discards immediately; otherwise it reports/discards and fails on end-of-input.

## State and Persistence Behavior
- All parser runtime state is in `yyParser`; generated parsers are reentrant as long as callers do not share one parser instance across threads unsafely.
- Debug tracing uses static globals `yyTraceFILE` and `yyTracePrompt`, so trace configuration is process-global for the generated parser.
- With `YYGROWABLESTACK`, the parser starts with inline `yystk0` and can allocate a heap stack using `YYREALLOC`, freeing it in `ParseFinalize()`. With fixed stacks, overflow calls generated `%stack_overflow` code.
- Error recovery state is `yyerrcnt`; it suppresses repeated syntax errors until three successful shifts.
- `ParseFinalize()` and `ParseFree()` run destructors for stack entries still present; error handling and stack pops also call generated destructors for discarded semantic values.
- Optional `YYCOVERAGE` records a static `yycoverage[YYNSTATE][YYNTOKEN]` matrix of observed state/lookahead pairs.

## Dependencies and Integration Points
- Requires generated definitions from `lemon.c`; the template alone is not standalone because most `%%` placeholders must be filled.
- Uses grammar-provided code for `%include`, `%destructor`, `%token_destructor`, `%default_destructor`, `%stack_overflow`, `%parse_failure`, `%syntax_error`, `%parse_accept`, and reduce actions.
- Memory allocation is injected with `YYREALLOC`/`YYFREE` and `YYMALLOCARGTYPE`; context and extra arguments are wired through generated `ParseARG_*` and `ParseCTX_*` macros.
- SQLite-generated parsers can enable `yytestcase()` and `YYCOVERAGE` to link parser table coverage to the surrounding test harness.

## Risks and Edge Cases
- Generated table constants must be internally consistent; wrong offsets or action ranges become assertion failures in debug builds and undefined parser behavior in release builds.
- Fallback token mappings assert that fallback chains terminate, so grammar fallback cycles are invalid.
- Destructor generation must match semantic value union members; wrong `%type` or alias handling can compile but destroy the wrong union member.
- Error recovery discards input and stack symbols, so grammar destructors must be correct to avoid leaks or double frees.
- Stack growth depends on grammar-provided allocator signatures matching `YYREALLOC`/`YYFREE` and optional `YYSIZELIMIT`.
- `ParseTrace()` globals are not per parser instance.

## Test Signals
- Compile a generated parser with assertions enabled and run grammar tests through successful parses, syntax errors, error recovery, end-of-input, and parser destruction.
- Enable `YYCOVERAGE` and inspect `ParseCoverage()` misses for untested parser states.
- Test `YYFALLBACK`, `YYWILDCARD`, fixed stack overflow, growable stack expansion, `%extra_argument`, `%extra_context`, and destructors.
- Validate memory cleanup with parser finalization after partial parse and after syntax-error discard paths.
