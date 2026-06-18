<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-v4l2_enc_idx.c -->
# sources/test-tools/stress-ng/test/test-v4l2_enc_idx.c research

Purpose: compile-time and smoke-runtime probe for stress-ng feature detection around `Linux V4L2 type `struct v4l2_enc_idx``. It lets the stress-ng build configure whether the platform exposes the requested header, type, syscall wrapper, or libc symbol before enabling code paths that depend on it.

Important APIs, types, and functions: the only function is `main()`. It includes `linux/videodev2.h`, declares the relevant object or arguments, and then declares `struct v4l2_enc_idx`, marks it used, and returns its size. There is no project-local type or helper API in this file; its public signal is successful compilation and, when the configure harness executes it, the process exit status.

Control flow: execution is linear: initialize any required local storage, call or size-check the probed API, and return the result. There are no loops, callbacks, or branches except simple cleanup/error paths where applicable.

State and persistence: state is limited to stack locals and any transient kernel/libc side effect from the probed call. No repository state is persisted. Runtime calls that touch the current directory, `/tmp`, `/dev/null`, or process wait state are intended as configure probes rather than application behavior.

Dependencies and integration: this file integrates with the stress-ng test/configure suite under `sources/test-tools/stress-ng/test`. A successful compile typically controls `HAVE_*` feature macros used by stress-ng stressors and shim code.

Risks: the API is Linux UAPI-header dependent; older or non-Linux systems may lack the type even if other V4L2 definitions exist. Runtime has no device interaction, so it cannot validate ioctl behavior.

Test signals: compile success confirms the header exposes `struct v4l2_enc_idx` for stress-ng V4L2 stressors; failure should disable only code paths requiring that exact type.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-v4l2_enc_idx.c -->
