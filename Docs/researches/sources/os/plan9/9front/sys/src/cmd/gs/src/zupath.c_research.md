# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/zupath.c

## Purpose
Implements Level 2 user path operators and insideness tests.

## Key Elements
Provides `infill`, `ineofill`, `instroke`, `inufill`, `inueofill`, `inustroke`, `uappend`, `ucache`, `ufill`, `ueofill`, `upath`, `ustroke`, and `ustrokepath`. Also exports `make_upath()` for building user path arrays from graphics paths.

## Behavior/Risks
Insideness tests install a hit-detection device after clipping either to a single device pixel around coordinates or to a supplied user path. User paths may be ordinary executable arrays or compact two-element encoded forms with numeric operands and opcode strings. The compact form supports repeat opcodes and validates argument counts against the user-path operator table. Optional matrices are supported for stroke operations. `ucache` is currently a no-op.

## Dependencies
Uses graphics path enumeration, clipping, path painting, path preservation, matrix parsing, binary number array decoding, dictionary lookup of executable path operators, and the Ghostscript hit-detection device.
