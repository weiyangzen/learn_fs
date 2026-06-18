# sources/user-network-fs/rclone/backend/sftp/sftp_unsupported.go

Purpose: placeholder file for unsupported platforms, currently `plan9`, so the package has buildable Go source and Go tooling does not report "no buildable Go source files".

Important APIs/types/functions: contains only package declaration and comments under build tag `plan9`.

Control flow: none at runtime. The build constraint selects this file instead of the main `!plan9` SFTP implementation.

State and persistence behavior: none.

Dependencies/integration: no imports. It integrates only with Go build tags.

Risks/test signals: low implementation risk, but important for cross-platform package hygiene. There are no tests needed beyond build selection.
