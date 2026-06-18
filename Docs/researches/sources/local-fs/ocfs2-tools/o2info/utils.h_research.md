# File Research: sources/local-fs/ocfs2-tools/o2info/utils.h

This header exposes common `o2info` utility functions for feature formatting, target method/open/close, file type and permission rendering, uid/gid lookup, stat timestamp extraction, human-readable time, symlink path formatting, and method detection.

It includes `o2info.h`, so callers inherit the method and operation type definitions. The header is used by the CLI and operation implementations as the shared utility boundary.
