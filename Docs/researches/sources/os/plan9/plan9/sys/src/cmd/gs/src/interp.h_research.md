# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/interp.h

Internal interface for interpreter initialization, systemdict entry helpers, stack allocation, GC, errors, and the top-level interpreter entry point.

Key behavior:
- Declares `i_initial_enter_name` and `i_initial_remove_name`, with macros using local `i_ctx_p`.
- Exposes `gs_interp_max_op_num_args` and `gs_interp_num_special_ops`.
- Declares `gs_interp_make_oper`.
- Declares `interp_reclaim`.
- Declares `gs_errorname` and `gs_errorinfo_put_string`.
- Declares `gs_interp_init`, `gs_interp_alloc_stacks`, `gs_interp_free_stacks`, `gs_interp_reset`, and `gs_interpret`.

Research notes:
- This header bridges `iinit.c`, `interp.c`, and code creating additional interpreter contexts.
- `gs_interpret` returns normal completion, input-needed statuses, quit/fatal codes, or PostScript error handling outcomes depending on `user_errors`.
