# sources/test-tools/syzkaller/pkg/config/config.go

Purpose: Small JSON config load/save helper with support for line comments starting with `#` and strict unknown-field rejection.

Important APIs/types/functions: `LoadFile`, `LoadData`, and `SaveFile`.

Control flow: `LoadFile` rejects empty filenames, reads file bytes, and delegates to `LoadData`. `LoadData` strips comment lines with a regexp, decodes JSON with `DisallowUnknownFields`, and wraps parse errors. `SaveFile` marshals indented JSON and writes via `osutil.WriteFile`.

State and persistence behavior: Reads and writes config files. No internal persistent state.

Dependencies/integration points: Used by syzkaller components that load manager/tool configs. Depends on standard JSON and `pkg/osutil`.

Risks: The comment stripper removes full lines beginning with optional whitespace and `#`; it does not support inline comments. Strict unknown fields are good for config hygiene but can break users with stale/extra fields.

Test signals: No direct tests in this file, but config merge tests cover adjacent package behavior; downstream config-loading tests likely exercise it.
