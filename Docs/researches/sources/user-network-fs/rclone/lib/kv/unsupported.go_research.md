# sources/user-network-fs/rclone/lib/kv/unsupported.go

Source read signal: reviewed complete local file (45 lines, sha256 f839941648342a49).

Purpose: Provides plan9/js unsupported stubs for the KV package.

Important APIs/types/functions: Defines empty `DB`, `Supported=false`, `Start`, `Get`, `Path`, `Do`, `Stop`, `IsStopped`, and `Exit`.

Control flow: Operations return `ErrUnsupported`, nil, or true stopped status.

State and persistence behavior: No state and no persistence.

Dependencies and integration points: Uses build tag `plan9 || js`, `context`, and `fs.Fs`. Allows code to compile while callers can branch on `Supported`.

Risks and test signals: The `Get` signature order differs from the supported implementation (`Get(f fs.Fs, facility string)` vs `Get(facility string, f fs.Fs)`), which is a compile-time risk on unsupported targets if callers use it. Cross-target builds should catch this.
