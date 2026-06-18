# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/interp.h

Internal interface header for `interp.c` and initialization code.

Key contents:
- Declares systemdict initialization helpers: `i_initial_enter_name`, `i_initial_remove_name`, and convenience macros using `i_ctx_p`.
- Exposes `gs_interp_max_op_num_args`.
- Exposes `gs_interp_num_special_ops`.
- Declares `gs_interp_make_oper`, which creates operators and assigns special fast-dispatch types when applicable.
- Declares `interp_reclaim`.
- Declares error support: `gs_errorname` and `gs_errorinfo_put_string`.
- Declares `gs_interp_init`, `gs_interp_alloc_stacks`, `gs_interp_free_stacks`, `gs_interp_reset`, and top-level `gs_interpret`.

Notable dependencies:
- Uses `i_ctx_t`, `ref`, `op_proc_t`, `gs_dual_memory_t`, `gs_ref_memory_t`, and `gs_context_state_t` from interpreter headers.

Research notes:
- This is a narrow internal ABI between interpreter initialization, context management, and the main execution loop.
- The special-operator count is shared with initialization so operator tables and packed execution agree.
