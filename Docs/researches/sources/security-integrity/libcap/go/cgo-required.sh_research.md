## sources/security-integrity/libcap/go/cgo-required.sh

Purpose: detects whether the Go runtime lacks `syscall.AllThreadsSyscall`, in which case libcap's Go security-state operations require cgo/libpsx for POSIX thread semantics.

Important APIs/functions: optional first argument selects `GO`; `go doc syscall | grep AllThreadsSyscall`.

Control flow: sets `GO` from argument or defaults to `go`, checks documentation output, echoes `1` if the symbol is absent and `0` if present.

State/persistence: no writes.

Dependencies/integration: Go toolchain and shell utilities; its output feeds build variables such as `CGO_REQUIRED`.

Risks: parsing `go doc` text is brittle and can be affected by localized or changed output; missing Go binary is treated the same as missing symbol.

Test signals: run against known Go versions before and after `AllThreadsSyscall` support and verify expected `1`/`0`.
