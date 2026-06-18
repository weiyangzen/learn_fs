# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/mouse.h

Purpose: Defines AT&T 320 / PS/2-style mouse command and response byte constants.

Key definitions:
- Commands: reset, resend, set defaults, disable/enable, set sampling/button mode, get device type, prompt/echo/stream/report/status/resolution/scaling commands.
- Response/status bytes: `MSE_ACK`, post-reset `MSE_AA`, `MSE_00`.

Relevance to subset A: Legacy device ABI, not filesystem-related.
