# File Research: sources/os/plan9/plan9/sys/src/cmd/ip/httpd/imagemap.c

Magic helper for server-side image maps. It reconstructs the request, binds the anonymous webroot, validates GET/HEAD and expectation headers, parses query coordinates, opens the map file named by the URI, and chooses a redirect target.

The parser supports NCSA and CERN-style map records with rectangles, circles, polygons, closest points, and defaults. If no target matches, it returns a small HTML “Nothing Found” page; otherwise it redirects to the selected destination.
