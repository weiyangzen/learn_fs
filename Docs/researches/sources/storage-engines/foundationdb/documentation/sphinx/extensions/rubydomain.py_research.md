# sources/storage-engines/foundationdb/documentation/sphinx/extensions/rubydomain.py

## Purpose
Implements the custom Sphinx `rb` domain used to document Ruby APIs in the FoundationDB docs. It provides Ruby directives, cross-reference roles, object registration, and a Ruby module index.

## Important APIs, Types, and Functions
`RubyDomain` registers object types, directives, roles, initial data, and `RubyModuleIndex`. `RubyObject` parses signatures, creates description nodes, registers targets, and adds index entries. Specialized directive classes cover module-level functions/globals, methods/constants, classes/exceptions, class methods, and attributes. `RubyModule` and `RubyCurrentModule` manage module context. `RubyXRefRole` normalizes link titles/targets. `rb_sig_re`, `rb_paramlist_re`, `separators`, and `ruby_rsplit()` drive Ruby name parsing.

## Control Flow
Sphinx invokes directive handlers during parsing. `handle_signature()` computes module/class/full names from options and `env.temp_data`, emits nodes, and parses optional arguments. `add_target_and_index()` records objects in `env.domaindata['rb']['objects']`. Cross references are resolved by `resolve_xref()`, which checks modules first and then searches object names with context-sensitive ordering.

## State and Persistence Behavior
Persistent build state lives in domain data: `objects` and `modules`. Temporary parsing context lives in `env.temp_data['rb:module']` and `env.temp_data['rb:class']`. `clear_doc()` removes stale entries for incremental rebuilds.

## Dependencies and Integration Points
Depends on Sphinx domains, roles, addnodes, object descriptions, doc fields, and docutils directives/nodes. Integrates through `setup(app).add_domain(RubyDomain)` and Sphinx config values such as `add_module_names` and `modindex_common_prefix`.

## Risks
The code targets older Sphinx APIs such as `env.warn` and legacy index tuple shapes. Signature parsing may reject or misparse complex Ruby syntax. Duplicate object descriptions warn but overwrite domain state. Cross-reference search order can resolve ambiguous names unexpectedly.

## Test Signals
Run a Sphinx build with Ruby directives, nested class/member docs, module indexes, duplicate descriptions, incremental rebuilds, tilde/leading-dot role targets, optional parameter lists, and unresolved-reference warnings treated as failures.
