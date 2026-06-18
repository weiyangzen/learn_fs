# File Research: sources/os/plan9/9front/sys/src/cmd/cpp/include.c

Include-file handling and generated line directives for cpp. It supports quoted includes, angled includes, macro-expanded include operands, dependency output, and `#pragma once`.

Important behavior:
- Searches absolute paths directly; quoted includes first search the current file directory.
- Include directories are searched from high index to low and may be marked `always` or deleted.
- Angled includes skip non-`always` entries until fallback current-directory lookup.
- `incblocked` prevents re-including files already seen by `#pragma once`.
- `genline()` emits `#line <n> "<path>"`, optionally prefixing the working directory for relative paths.
- `setobjname()` formats dependency target names for `-M`.
