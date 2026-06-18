# File Research: sources/os/plan9/9front/sys/src/cmd/map/libmap/cylindrical.c

Implements a cylindrical projection with x as negative longitude and y as tangent latitude (`sin/cos`). It rejects latitudes beyond about 80 degrees. `cylindrical()` returns `Xcylindrical()`.
