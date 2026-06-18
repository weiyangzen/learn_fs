# sources/security-integrity/selinux/python/sepolgen/tests/test_interfaces.py

## Purpose
This test file validates extraction and expansion of SELinux reference-policy interfaces into access-vector summaries. It checks parameter typing, interface parsing, nested interface-call expansion, and export/import of interface metadata.

## Important Tests And Exercised APIs
`TestParam` validates `interfaces.Param`, including `$N` validation, numeric extraction, and default source-type classification. `TestAVExtractPerms` exercises `av_extract_params()` across source parameters, target parameters, process class special cases, and directory target behavior.

`compare_avsets()` builds an `AccessVectorSet` from a list and compares it to another set after sorting. `TestInterfaceSet.test_simple()` parses a simple interface, adds headers into `InterfaceSet`, and checks interface name, access vectors, and required parameter metadata. `test_expansion()` validates nested interface expansion across `foo`, `map`, and `hard_map`. `test_export()` writes `InterfaceSet.to_file()` output and reads it back with `from_file()`.

## Control Flow
The test embeds reference-policy interface text with `interface(...)`, `gen_require`, `allow`, `optional_policy`, `tunable_policy`, and nested interface calls. It parses text through `refparser.parse()`, then `InterfaceSet.add_headers()` extracts and expands access data. Export writes to a local file named `output`, then reimports and checks expected interface names.

## State And Persistence
Most state is in memory within `InterfaceSet.interfaces`, each interface's `.access` and `.params`. `test_export()` persists a temporary `output` file in the test directory, which the Makefile cleans.

## Dependencies And Integration Points
It depends on `sepolgen.access`, `sepolgen.interfaces`, `sepolgen.policygen`, `sepolgen.refparser`, and `sepolgen.refpolicy`. The parser dependency indirectly exercises `yacc.py`. The exported interface data is also consumed by matching and CLI tooling.

## Risks And Edge Cases
String snippets include optional and tunable policy blocks but assertions mostly focus on allow rules and interface names, so conditional-policy semantics are not deeply validated. The export test only checks names after round-trip, not full access vectors or parameter metadata. File output is fixed-name and working-directory dependent.

## Test Signals
This is the strongest test signal for interface expansion and parameter inference. It confirms nested calls substitute parameters correctly and duplicate/no-op calls do not unexpectedly add access.
