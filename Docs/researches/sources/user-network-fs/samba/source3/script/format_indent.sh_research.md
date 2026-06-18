# sources/user-network-fs/samba/source3/script/format_indent.sh

Purpose: shell wrapper around GNU `indent` with Samba C formatting options.

Important APIs, types, and functions: invokes `indent -npro -kr -i8 -ts8 -sob -l80 -ss -ncs "$@"`.

Control flow: no branching; passes all arguments directly to `indent`.

State and persistence: modifies files according to `indent` behavior.

Dependencies and integration: requires an `indent` implementation compatible with these options.

Risks: can create broad formatting churn. Behavior depends on the installed `indent` version.

Test signals: run on a copied C file, check diff shape, and verify unsupported-option behavior on target platforms.
