# sources/user-network-fs/rclone/backend/oracleobjectstorage/oracleobjectstorage_unsupported.go

Purpose: provides a minimal buildable package for unsupported platforms where the real Oracle Object Storage backend is excluded.

Important APIs/types/functions: no runtime APIs are declared. The file contains build constraints for `plan9 || solaris || js` and a `package oracleobjectstorage` declaration with package documentation.

Control flow: none at runtime. Go's build tag resolver selects this file when supported-platform files are excluded.

State and persistence: no local or remote state.

Dependencies/integration: no imports. It integrates only with Go build constraints and rclone's expectation that the backend package remains discoverable in the source tree.

Risks/test signals: if future files in this package omit compatible build tags, unsupported-platform builds could again fail with no buildable source or conflicting definitions. The test signal is successful package loading/building for Plan 9, Solaris, and JavaScript/WASM targets.
