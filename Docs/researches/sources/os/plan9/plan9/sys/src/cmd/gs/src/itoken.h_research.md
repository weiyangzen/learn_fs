# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/itoken.h

Purpose: declares exported token-handling procedures from `ztoken.c`.

APIs:
- `ztokenexec_continue` resumes token execution after a procedure stream refill or callout.
- `ztoken_handle_comment` handles scanner comment/DSC-comment returns, with optional scanner-state saving and file pushing for continuations.
- `ztoken_scanner_options` updates cached scanner options after `setuserparams`.

The header ties the low-level scanner return codes to interpreter operators and execution-stack continuation flow.
