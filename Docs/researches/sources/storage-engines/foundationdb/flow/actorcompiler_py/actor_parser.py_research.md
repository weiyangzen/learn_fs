## sources/storage-engines/foundationdb/flow/actorcompiler_py/actor_parser.py

Purpose: this Python file is the parser/source-to-source front end for the Python actor compiler port. It tokenizes C++ actor source, parses actor-language constructs into Python dataclasses, and splices generated C++ from `actor_compiler.py` back into the output stream.

Important types and APIs: `ErrorMessagePolicy`, `Token`, `TokenRange`, `BracketParser`, `AngleBracketParser`, and `ActorParser` mirror the C# implementation. `ActorParser.write(writer, destFileName)` scans the source and expands `ACTOR`, `SWIFT_ACTOR`, and `TEST_CASE`. Parsing helpers include `parse_actorHeading`, `parse_test_caseHeading`, `parse_declaration`, `parse_var_declaration`, `parse_wait_statement`, `parse_for_statement`, `parse_code_block`, `parse_statement`, and `parse_class_context`.

Control flow: initialization tokenizes via ordered regular expressions and annotates brace/paren depth and source lines. `write` clears class-name global state, writes `POST_ACTOR_COMPILER`, tracks output line numbers and class nesting, invokes `ActorCompiler` for actor constructs, merges UID objects, and otherwise copies tokens through. Parsing distinguishes forward declarations from definitions, fills actor namespace/enclosing-class data, warns on no-wait actors, and rejects unsupported actor-local syntax.

State and persistence behavior: parser state is in memory: token list, source path, line-number flag, error policy, probe flag, UID map, and a private `_parse_end` cursor. It does not write files directly; `__main__.py` owns persistence.

Dependencies and integration points: imports `ActorCompiler`, parse-tree dataclasses, and `ActorCompilerError`. It must remain grammar-compatible with C# actor source accepted by the original compiler, including templates, attributes, `UNCANCELLABLE`, `[[flow_allow_discard]]`, `[[nodiscard]]` insertion, `state`, `wait`, `waitNext`, `choose`/`when`, loops, `try`/`catch`, and tests.

Risks: migration drift is the major risk. Differences from C# naming/casing are internal, but output behavior must match. The parser uses regex tokenization and simple declaration splitting; complex C++ types, nested templates, attributes, and initializers are sensitive. `parse_wait_statement` sets `is_wait_next` by scanning initializer tokens after accepting either wait keyword; this is clear but should be covered. `parse_compound_statement` assumes non-braced single statements can be parsed from `toks.skip(1)`, matching C# behavior but easy to break if token range semantics change.

Test signals: compare generated outputs against the C# compiler, especially for line directives, attributes, namespace/class nesting, template actors, forward declarations, `TEST_CASE`, state declarations, waits, `waitNext`, `choose`, illegal keyword errors, and no-wait warnings.
