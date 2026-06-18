# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/macgenmcpxml.sh

## Purpose
Shell generator for a CodeWarrior XML project file for classic Mac OS / Carbon Ghostscript library builds.

## Main Structure
- Emits a full XML/DTD header with `WriteXMLHeader`.
- Helper functions emit `<FILE>`, `<FILEREF>`, scalar settings, path settings, target setting lists, target definitions, and project groups.
- Parses command-line `.o` arguments, strips paths, converts them to `.c`, and builds `CFILES`.
- Defines Carbon and classic library lists, target names, and emits a project with Carbon debug and classic debug targets.

## Important Settings
- Compiler prefix header is selected by target:
  - Carbon debug: `macos_carbon_d_pre.h`
  - Carbon non-debug: `macos_carbon_pre.h`
  - Classic debug: `macos_classic_d_pre.h`
  - Classic non-debug: no prefix value.
- Search paths include project `src`, `obj`, root, CodeWarrior MacOS Support, MSL, jbig2dec, and Jasper include paths.
- PPC project type is `SharedLibrary`.

## Integration Notes
- Invoked from `macos-mcp.mak` using the object list from `ldt.tr`.
- Output is redirected to `ghostscript.mcp.xml`, then marked as CodeWarrior text metadata by `SetFile`.

## Risks and Edge Cases
- Library filenames with spaces are explicitly noted as unsupported by the group-generation loop.
- XML is emitted by unescaped `echo`; paths containing XML-significant characters would break the output.
- The parser only recognizes `*.o` arguments and ignores other link tokens except literal backslash continuations.
