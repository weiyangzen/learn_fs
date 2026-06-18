# File Research: sources/local-fs/ocfs2-tools/fsck.ocfs2/problem.c

Purpose: implements fsck user prompting, including interactive single-character input, defaults, non-interactive answers, and abort handling.

Read coverage: complete file read, 165 lines.

Key responsibilities:
- Prints a problem code tag and caller-provided repair question.
- Applies non-interactive answers from fsck state when `ost_ask` is disabled.
- Displays default yes/no hints based on `PY` / `PN` flags.
- Reads one terminal character with canonical mode and echo disabled.
- Treats Ctrl-C and Escape as cancellation, exiting with fsck error/canceled status.
- Accepts space or newline as the configured default answer.

Important entry points:
- `prompt_input()` is the exported prompting implementation behind problem prompts.
- `read_a_char()` sets terminal mode and reads a single character.
- `handle_sigint()` records interrupt state for the input loop.

Dependencies:
- Uses POSIX `termios`, `sigaction`, `read`, `tolower`, and fsck state flags from `problem.h` / `fsck.h`.

Risk and edge cases:
- `read_a_char()` installs a one-shot SIGINT handler and restores terminal settings after the read.
- If both default-yes and default-no flags are supplied, default-yes is cleared.
- The file comments call out missing persistent answers for repeated identical questions.
