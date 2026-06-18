# File Research: sources/os/plan9/9front/sys/src/cmd/ip/httpd/imagemap.c

Magic helper for old-style server-side image maps. It accepts GET/HEAD, parses the query coordinates, opens the map file named by the URI, and selects a destination URL using NCSA or CERN-style map records.

Supported shapes include rectangles, circles, polygons, points, and default targets. It returns a redirect to the selected target or emits a small HTML “Nothing Found” response when no target matches.
