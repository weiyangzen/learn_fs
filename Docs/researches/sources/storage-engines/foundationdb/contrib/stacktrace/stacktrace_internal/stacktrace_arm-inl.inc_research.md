# sources/storage-engines/foundationdb/contrib/stacktrace/stacktrace_internal/stacktrace_arm-inl.inc

## Purpose
This file implements stack unwinding for 32-bit ARM builds that retain frame pointers. It is a compact frame-chain walker designed for the common single-instruction-set case.

## Important APIs, Types, And Functions
`NextStackFrame<STRICT_UNWINDING>` reads the previous stack frame from `old_sp[-1]`, validates ordering, maximum frame size, and pointer alignment, and returns `nullptr` on implausible transitions. `StacktraceArmDummyFunction` is a noinline assembly barrier that forces the link register to be saved. `UnwindImpl<IS_STACK_FRAMES, IS_WITH_CONTEXT>` records return addresses and optional frame sizes.

## Control Flow
`UnwindImpl` obtains the current frame address with `__builtin_frame_address(0)`, calls the dummy function so the current function's return address is materialized on the stack, then walks frames until `max_depth` or a failed validation. It records `*sp` as the return PC and computes frame sizes when requested. `min_dropped_frames` is estimated by walking up to 200 additional frames.

## State And Persistence
There is no persistent state. All state is local to the unwind call.

## Dependencies And Integration Points
The code depends on GCC-compatible frame-address builtins, ARM frame layout, and the common stacktrace template signature. It is selected by the stacktrace config for `__arm__` when frame pointers are present.

## Risks
The header explicitly warns that mixed ARM/Thumb interworking can break frame-pointer discovery because caller and callee may use different frame-pointer registers. It does not consume `ucontext_t`, so signal unwinding support is weaker than the x86/AArch64/PowerPC implementations. Builds without frame pointers error or route away from this file.

## Test Signals
Coverage should include ARM and Thumb-mode builds separately, non-leaf and leaf frames, strict and non-strict frame-size validation, and capped-depth dropped-frame counting.
