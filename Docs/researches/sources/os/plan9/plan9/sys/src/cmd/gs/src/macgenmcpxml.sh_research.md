# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/macgenmcpxml.sh

`macgenmcpxml.sh` generates a Metrowerks CodeWarrior XML project file for classic Mac OS and Carbon Ghostscript library targets. It writes XML directly to stdout using shell functions.

The script defines emitters for the XML header/DTD, file entries, file references, scalar settings, recursive search-path settings, target settings, targets, and groups. `WriteSETTINGLIST` encodes CodeWarrior panel settings for target output, access paths, build extras, PPC project metadata, C compiler settings, warnings, code generation, optimizer, linker, and PEF output.

At runtime it scans command-line arguments for `.o` file names, strips path prefixes, converts them to `.c`, and stores them in `CFILES`. It then defines Carbon and Classic library sets, target names, and writes a project with Carbon Debug and Classic Debug targets. Prefix headers are selected by target/output: Carbon debug uses `macos_carbon_d_pre.h`, Carbon final would use `macos_carbon_pre.h`, Classic debug uses `macos_classic_d_pre.h`, and non-debug Classic has no prefix.

Integration is through `macos-mcp.mak`, which passes the generated link trace into this script and redirects output to `ghostscript.mcp.xml`. Risks are direct XML string interpolation without escaping, fragile shell word splitting, and an in-file note that library filenames containing spaces are not handled by the library group loop.
