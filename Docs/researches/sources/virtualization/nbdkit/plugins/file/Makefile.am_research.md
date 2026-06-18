# File Research: sources/virtualization/nbdkit/plugins/file/Makefile.am

Build definition for the production file plugin.

Key contents:
- Builds `nbdkit-file-plugin.la`.
- Uses `file.c` on non-Windows and `winfile.c` on Windows.
- Includes common nbdkit, replacements, and utility headers.
- Links common utility and compatibility libraries.
- Generates documentation with magic-parameter insertion when POD is available.
