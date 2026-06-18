# sources/storage-engines/foundationdb/contrib/stacktrace/stacktrace_internal/stacktrace_aarch64-inl.inc

## Purpose
This inline implementation provides the AArch64 frame-pointer unwinder used by the amalgamated stacktrace code when `__aarch64__` is selected and frame pointers are available. It walks the standard AArch64 frame chain and can use Linux signal context to unwind across signal frames.

## Important APIs, Types, And Functions
`GetKernelRtSigreturnAddress` memoizes the VDSO `__kernel_rt_sigreturn` address using `VDSOSupport`. `ComputeStackFrameSize` computes byte distance between two frame pointers and returns `kUnknownFrameSize` when ordering is invalid. `NextStackFrame<STRICT_UNWINDING, WITH_CONTEXT>` validates the next frame pointer, including 16-byte alignment and frame-size limits. `UnwindImpl<IS_STACK_FRAMES, IS_WITH_CONTEXT>` captures PCs and optional frame sizes for the public stacktrace API.

## Control Flow
`UnwindImpl` starts from `__builtin_frame_address(0)`, skips itself, and repeatedly calls `NextStackFrame`. AArch64 frames store the previous frame pointer in word 0 and return address in word 1; the implementation records the previous return address after stepping. In Linux signal-context mode, if the current return address is `__kernel_rt_sigreturn`, the unwinder reads register 29 from `ucontext_t` as the pre-signal frame pointer and skips normal frame-size checks for that transition.

## State And Persistence
The only retained state is a static atomic memoized VDSO signal-return address. No durable persistence exists.

## Dependencies And Integration Points
It depends on GCC frame-address builtin, AArch64 ABI frame layout, Linux `ucontext_t` register naming, `AddressIsReadable`, and optional VDSO support. It is included through `ABSL_STACKTRACE_INL_HEADER` and must match the common `UnwindImpl` template signature.

## Risks
The unwinder requires reliable frame pointers; `NO_FRAME_POINTER` selects an unimplemented path for AArch64 elsewhere. Bad or corrupt frame chains can still yield incomplete or bogus traces, though alignment and size checks reduce the blast radius. Signal unwinding is Linux-specific and assumes VDSO symbols and `uc_mcontext.regs[29]` semantics.

## Test Signals
Relevant tests include ordinary call-stack capture on AArch64, capture from a signal handler, alternate signal stacks, strict frame-size reporting via `GetStackFrames`, and `min_dropped_frames` behavior when depth is capped.
