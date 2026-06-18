# Research: sources/security-integrity/selinux/python/sepolicy/sepolicy/interface.py

## Purpose
`interface.py` exposes SELinux policy interface metadata. It reads generated policy XML or converts `.if` interface files to XML, lists interfaces, identifies admin and user-role interfaces, formats interface summaries, generates compile-test TE modules, and optionally invokes the SELinux development Makefile to validate interface compilation.

## Important APIs and control flow
The public surface is declared in `__all__`: `get_all_interfaces()`, `get_interfaces_from_xml()`, `get_admin()`, `get_user()`, `get_interface_dict()`, `get_interface_format_text()`, `get_interface_compile_format_text()`, `get_xml_file()`, and `interface_compile_test()`.

`get_all_interfaces(path="")` either delegates to `sepolicy.get_methods()` for installed policy or converts/parses a supplied interface file. `get_interface_dict(path)` parses XML layers/modules/interfaces/templates with `xml.etree.ElementTree`, storing each interface name as `[param_names, summary_text, "interface"|"template"]` in a module-global cache. `get_admin()` and `get_user()` filter interface names ending in `_admin` or `_role`; installed-policy mode returns stripped domain prefixes, while path mode returns full matching interface names and checks role interfaces against `sepolicy.get_all_types()`. Formatting helpers render human-readable signatures or compile-call stubs using `.templates.test_module.dict_values`. `get_xml_file(if_file)` shells out to `/usr/share/selinux/devel/include/support/segenxml.py`. `interface_compile_test()` writes temporary compile-test files, runs `make -f /usr/share/selinux/devel/Makefile compiletest.pp`, reports failures, and deletes generated files.

## State and persistence
The only module state is `interface_dict`, a global cache that persists after the first parse. `interface_compile_test()` writes and deletes `compiletest.te`, `compiletest.fc`, `compiletest.if`, and `compiletest.pp` in the current working directory; failed or interrupted runs could leave files behind. `get_xml_file()` and compile tests depend on installed SELinux development files.

## Dependencies and integration points
Dependencies include `re`, `sys`, `sepolicy`, gettext, XML parsing, `subprocess.getstatusoutput` or legacy `commands`, `os`, templates from `.templates.test_module`, the `segenxml.py` converter, and the SELinux devel Makefile. It integrates with the main `sepolicy` interface method cache and with policy development tooling that validates interface calls.

## Risks and edge cases
`get_interface_dict()` caches without considering the path argument, so the first parsed policy XML is returned for all later paths. XML parsing assumes `summary` nodes exist and have text. `get_xml_file()` builds a shell command with an unquoted path, so interface file paths containing shell metacharacters can change command behavior. `interface_compile_test()` writes fixed filenames in the current directory, so concurrent runs collide and user files with the same names can be overwritten/deleted. It shells out through `getstatusoutput()` and depends on system Python/devel paths. Several error paths call `sys.exit(1)`, which is inconvenient for library callers. Installed-policy and path modes return different name shapes for admin/user helpers.

## Test signals
Tests should parse fixture XML containing interfaces, templates, parameters, and summaries; validate `get_admin()`/`get_user()` in both path and installed-policy modes; check cache behavior when different paths are requested; verify formatting against `test_module.dict_values`; mock `getstatusoutput()` for XML conversion and compile success/failure; and run compile-test logic in a temporary directory to ensure cleanup and no accidental overwrite.
