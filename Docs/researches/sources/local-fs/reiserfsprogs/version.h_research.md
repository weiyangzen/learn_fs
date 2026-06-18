# File Research: sources/local-fs/reiserfsprogs/version.h

Tiny shared version/banner header for ReiserFS tools.

Major responsibilities:
- Defines `print_banner(prog)` as a macro that writes `<program> <VERSION>` to stderr.

Dependencies and interactions:
- Included by resize and tune headers.
- Requires `VERSION` to be defined by build configuration or included headers.

Risks and notes:
- Macro expands directly to `fprintf(stderr, ...)`; callers must include stdio-compatible declarations through surrounding headers.
