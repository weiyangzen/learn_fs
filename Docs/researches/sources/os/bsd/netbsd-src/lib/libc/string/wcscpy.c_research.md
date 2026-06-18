# File Research: sources/os/bsd/netbsd-src/lib/libc/string/wcscpy.c

Implements `wcscpy()`. It copies wide characters from source to destination until and including the terminating NUL, then returns the original destination.

No overlap or bounds protection is provided.
