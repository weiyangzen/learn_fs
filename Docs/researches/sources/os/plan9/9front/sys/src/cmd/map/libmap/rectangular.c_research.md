# File Research: sources/os/plan9/9front/sys/src/cmd/map/libmap/rectangular.c

Implements rectangular/equirectangular projection with a standard parallel scale. `rectangular(par)` stores `cos(par)` as longitude scale and rejects near-polar scales below 0.1. `Xrectangular()` maps x to scaled negative longitude and y to latitude.
