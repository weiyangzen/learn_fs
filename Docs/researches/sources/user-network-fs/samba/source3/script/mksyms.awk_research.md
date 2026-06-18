# sources/user-network-fs/samba/source3/script/mksyms.awk

Purpose: parses C header files and emits a linker version-script style export list.

Important APIs, types, and functions: AWK state `inheader` tracks multi-line prototypes; it prints `global:` entries for extern variables and function prototypes, then `local: *;`.

Control flow: skip static, typedef, and non-symbol-leading lines; handle simple `extern type name;`; detect one-line function prototypes; enter multiline mode after detecting an opening paren until a closing prototype line is seen.

State and persistence: writes generated version script to stdout. Tracks current filename for comments.

Dependencies and integration: used by `mksyms.sh` with sorted unique header inputs.

Risks: regex-based C parsing can miss complex declarations, macros, attributes, function pointers, or unusual formatting. It may export unintended names if prototypes are nonstandard.

Test signals: headers with extern variables, single-line prototypes, multiline prototypes, static/typedef skips, attributes, and function pointers.
