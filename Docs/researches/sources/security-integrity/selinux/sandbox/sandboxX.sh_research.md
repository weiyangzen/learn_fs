# sources/security-integrity/selinux/sandbox/sandboxX.sh
# sources/security-integrity/selinux/sandbox/sandboxX.sh

Purpose: shell launcher for graphical sandbox sessions.

Important APIs and control flow: computes a title from current SELinux context and `~/.sandboxrc`, sets Wayland/native flag, screen size, and DPI defaults, writes an Openbox config disabling decorations/maximizing windows, then either starts `Xephyr` or `Xwayland` and runs `/usr/share/sandbox/start ~/.sandboxrc` inside the nested display, or directly runs the start helper for native Wayland. It creates `~/seremote` to pass display environment into commands and kills the process group on nested server exit.

State and persistence: writes `~/.config/openbox/rc.xml` and `~/seremote` inside the sandbox home, sets display-related environment variables, and starts nested display processes.

Dependencies and integration points: invoked by Python `sandbox` via `seunshare`; depends on `id`, `secon`, `Xephyr`, `Xwayland`, Openbox, and `start`.

Risks and test signals: uses `eval` on constructed display command and unquoted parameter tests (`[ -z $1 ]`), so unusual arguments could affect shell parsing. No tests cover graphical launch.
