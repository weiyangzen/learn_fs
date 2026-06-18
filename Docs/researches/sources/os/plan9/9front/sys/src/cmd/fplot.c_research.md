# File Research: sources/os/plan9/9front/sys/src/cmd/fplot.c

## Purpose
Plots mathematical functions interactively or emits a Plan 9 RGB image.

## Key Elements
Lexes expressions over variable `x`, constants `pi`/`π`/`e`, arithmetic operators, and math functions; converts to reverse-polish code; computes stack depth; draws adaptively subdivided graph segments; computes axes/ticks/labels; supports color image output with `-c`, range `-r`, size `-s`, axis suppression `-a`, mouse zoom/unzoom/readout, and `y` auto-fit.

## Dependencies
Uses Plan 9 draw/event APIs and libc math functions, with floating-point exceptions for divide-by-zero/invalid masked.

## Behavior/Risks
Expression parser is compact and does not handle unary minus distinctly in token context beyond operator precedence. The `min` operator table entry points to `omax`, which appears to make `min` behave as max. Interactive readout finds nearest drawn pixel by scanning the full pixel map.
