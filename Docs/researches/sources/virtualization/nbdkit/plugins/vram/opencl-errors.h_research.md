# File Research: sources/virtualization/nbdkit/plugins/vram/opencl-errors.h

Provides OpenCL error-code stringification for the VRAM plugin.

Key behavior:
- Defines `opencl_errstr(cl_int err)` as a switch over standard OpenCL errors and `CL_PLATFORM_NOT_FOUND_KHR`.
- Returns `"unknown OpenCL error"` for unrecognized codes.
- Defines `opencl_to_error(err, what)` macro that emits `nbdkit_error("%s: error %d (%s)", ...)`.

Dependencies:
- OpenCL constants must be visible before including this header.
- nbdkit logging for the macro.

Notes:
- This is a local substitute because OpenCL does not provide a standard error-to-string API.
