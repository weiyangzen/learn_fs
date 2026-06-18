# sources/test-tools/syzkaller/pkg/codesearch/testdata/source0.h

Purpose: Header fixture included by `source0.c` to test extraction of comments, static inline functions, structs, typedefs, unions, enums, and duplicated function names across files.

Important APIs/types/functions: Declares `function_with_comment_in_header`, `same_name_in_several_files`, static inline `func_in_header`, `struct some_struct`, typedef `some_struct_t`, `struct some_struct_with_a_comment`, anonymous/ named struct typedefs, `union some_union`, `enum some_enum`, and `some_enum_t`.

Control flow: Only `func_in_header` has executable code, returning 0. Most content drives type/entity extraction.

State and persistence behavior: Source declarations are reflected in `source0.c.json` because the header is included by the compiled C fixture.

Dependencies/integration points: Included by `source0.c`; used for definition lookup and struct layout queries.

Risks: Header definitions are extracted through a compile unit, so changes to inclusion or compile database can affect visibility. Static inline functions in headers have special visibility rules in `findDefinition`.

Test signals: Validates header comments, type definitions, field offsets, union layout, enum/typedef extraction, and header-static function calls.
