## sources/test-tools/syzkaller/sys/empty.go

Purpose: placeholder package file that keeps the `sys` package buildable before generated descriptions are available.

Important APIs/types/functions: none.

Control flow: no runtime behavior.

State and persistence: none.

Dependencies/integration: supports Go package build integrity for `github.com/google/syzkaller/sys`.

Risks: if generated registration files are absent, the build still succeeds but targets may not be registered.

Test signals: build-only signal; no direct tests are needed.
