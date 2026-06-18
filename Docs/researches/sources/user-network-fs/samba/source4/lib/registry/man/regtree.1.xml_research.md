# sources/user-network-fs/samba/source4/lib/registry/man/regtree.1.xml

This DocBook man page documents `regtree`, a text-mode registry viewer that prints all contents of a Windows registry file. It documents backend and credential options plus `--fullpath` and `--no-values`, which control output path formatting and whether values are printed. It links related tools such as `gregedit`, `regshell`, `regdiff`, and `regpatch`.

There is no executable control flow in the XML; it describes read-only traversal behavior over registry backends. Persistence is not mutated by the tool, but output reflects the selected registry file or backend. Integration points are registry backend loading, Samba credential parsing for remote registries, and the registry enumeration APIs.

Risks are documentation drift around option names and backend support. Since `regtree` is often used to validate `regpatch` or inspect generated hives, output stability matters. Test signals include manpage generation, `regtree --help`, full-path/no-values output comparison, and traversal of hives containing default values and nested keys.
