<!-- BEGIN_FILE_RESEARCH: sources/test-tools/pynfs/xdr/xdrgen.py -->
# sources/test-tools/pynfs/xdr/xdrgen.py

Purpose: a Python RPC/XDR protocol compiler that parses `.x` files using PLY and generates Python constants, type classes, packers, and unpackers around `xdrlib`/`xdrlib3`.

Important APIs/types/functions: lexer token functions include `t_ID`, `t_CONST16`, `t_CONST8`, `t_CONST10`, comment handlers, and `t_error`. Parser rules cover XDR constants, typedefs, enum/struct/union declarations, arrays, pointers-as-variable arrays, and RPC `program/version/procedure` declarations. Core model classes are `Case_Spec`, base `Info`, `const_info`, `enum_info`, `struct_info`, `union_info`, and `type_info`; these produce `const_output`, `type_output`, `pack_output`, `unpack_output`, and XDR body text. `run(infile, filters=True, pass_attrs=True, debug=False)` is the public generation entry point.

Control flow: module import builds a lexer. `run` sets global options, derives output basenames from the input file, clears `name_dict`, reads the input, builds a PLY yacc parser, parses, then writes three generated modules: `<base>_const.py`, `<base>_type.py`, and `<base>_pack.py`. Generated packer/unpacker classes subclass `xdrlib.Packer` and `xdrlib.Unpacker` and include optional enum/array checks.

State and persistence: heavy use of globals (`name_dict`, `error_occurred`, output file names, generation options). Output files are overwritten in the current process directory. Parser symbols store line numbers and sort numbers to preserve source order.

Dependencies and integration: depends on PLY, `xdrlib3` or stdlib `xdrlib`, and Python package-relative imports in generated files. `rpc/setup.py` calls `xdrgen.run` during build.

Risks: global `error_occurred` is initialized once and not reset inside `run`, so one failed parse can poison later parses in the same process. Generation is not atomic and can leave partial files. The parser ignores RPC program/procedure code generation beyond constants. `StringIO` and `keyword` imports are unused, and broad `except` clauses hide import issues. Test signals: run the generator on representative `.x` files, import all three generated modules, instantiate generated structs/unions, and round-trip pack/unpack with bounds checking on arrays and enums.
<!-- END_FILE_RESEARCH: sources/test-tools/pynfs/xdr/xdrgen.py -->
