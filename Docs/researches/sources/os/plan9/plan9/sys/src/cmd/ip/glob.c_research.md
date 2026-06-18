# File Research: sources/os/plan9/plan9/sys/src/cmd/ip/glob.c

Standalone glob implementation used by Plan 9 IP commands. It expands path patterns without fixed path-element size limits by converting each path component into a regular expression and walking candidate directories one component at a time.

It supports absolute and relative patterns, `*`, `?`, escaped regexp metacharacters, directory-only `.` matching, incremental result construction through `Globlist`, and iterator-style result consumption with `globiter`.
