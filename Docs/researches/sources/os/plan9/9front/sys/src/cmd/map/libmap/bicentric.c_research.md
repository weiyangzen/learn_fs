# File Research: sources/os/plan9/9front/sys/src/cmd/map/libmap/bicentric.c

Implements a bicentric projection parameterized by a center latitude. It rejects latitudes/longitudes near singularities, computes x from longitude tangent scaled by center cosine, y from latitude over `cos(lat)*cos(lon)`, and returns visible status based on radius squared <= 9.

`bicentric()` rejects parameters above 89 degrees, stores the absolute center latitude, and returns `Xbicentric`.
