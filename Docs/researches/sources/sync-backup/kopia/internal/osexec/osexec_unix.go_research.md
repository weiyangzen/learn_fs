# sources/sync-backup/kopia/internal/osexec/osexec_unix.go

Purpose: Unix implementation that prevents child commands from receiving terminal interrupt signals intended for Kopia.

Important APIs/types/functions: `DisableInterruptSignal(c *exec.Cmd)`.

Control flow: sets `SysProcAttr.Setpgid = true` so the child runs in a separate process group.

State and persistence behavior: mutates the `exec.Cmd` before start; no persistent state.

Dependencies and integration points: depends on `syscall.SysProcAttr` and is used before starting external helpers.

Risks and test signals: callers must invoke it before `Start`; tests should confirm process group isolation on Unix where feasible.
