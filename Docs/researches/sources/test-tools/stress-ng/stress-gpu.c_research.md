# sources/test-tools/stress-ng/stress-gpu.c

## Purpose
`stress-gpu.c` implements a headless GPU rendering stressor using GBM, EGL, and OpenGL ES 2. It renders colored triangles, optionally uploads textures each frame, drives fragment shader work through a configurable loop count, and samples GPU frequency when pthread support is available.

## Important APIs, Types, And Functions
Options include `gpu-devnode`, `gpu-frag`, `gpu-tex-size`, `gpu-upload`, `gpu-xsize`, and `gpu-ysize`. `compile_shader()` and `load_shaders()` create the GLES program from embedded vertex and fragment shaders. `get_config()`, `egl_init()`, and `gles2_init()` set up the GBM/EGL surface, context, attributes, texture buffer, and draw state. `stress_gpu_run()` performs texture uploads, clears, draws six vertices, and calls `glFinish()`. `stress_gpu_child()` performs the full setup/run/cleanup under `stress_oomable_child()`. `stress_gpu_supported()` checks that the render node opens.

## Control Flow
The child blocks `SIGALRM`, temporarily suppresses stderr noise from graphics stacks, disables Mesa shader cache/logging, reads options, opens the render node, creates GBM/EGL/GLES state, optionally starts a frequency-sampling pthread, waits at the sync barrier, then loops draw/upload/finish until alarm or stop. It increments bogo ops per rendered frame and records average GPU MHz when samples are available.

## State And Persistence
Global process state includes `program`, `display`, `surface`, GBM handles, `gpu_card`, and `teximage`. Environment variables alter Mesa runtime behavior. No persistent files are written by the stressor, but it reads `/sys/class/drm/cardN/gt_cur_freq_mhz`.

## Dependencies And Integration Points
The stressor is compiled only with EGL headers/libs, GLES2, GBM, and optional pthreads. It integrates with stress-ng OOM isolation, metrics, process state, signal, and settings helpers.

## Risks
Driver behavior varies widely; EGL/GBM setup failures should skip rather than fail. Cleanup is partial because GL/EGL objects are not explicitly destroyed before process exit. Global graphics state would be unsafe across threads, but stress-ng workers are separate processes. Large texture sizes can exhaust memory or hit GL limits.

## Test Signals
Build feature gating, successful skip on systems without `/dev/dri/renderD128`, shader compile/link success, GL error-free loops, restored stderr, valid `gpu-card` parsing, and nonzero frame/GPU-frequency metrics are the main signals.
