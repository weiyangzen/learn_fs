# File Research: sources/os/plan9/plan9/sys/src/cmd/calls.c

Static C call graph printer. It preprocesses each input file with `cpp -+`, scans the resulting C token stream, records function definitions and call sites, and prints indented call trees.

Core structures are `Rname` for named functions, `Rinst` for call instances, and hash buckets for lookup. The scanner skips comments, strings, character constants, preprocessor line markers, reserved words, and extern declarations, using brace depth to distinguish definitions from calls.

Options include roots via `-f`, APE include mode `-p`, terse/full output `-t/-v`, output width `-w`, and forwarded `-D/-I/-U` cpp options. Output marks recursion and external functions; default roots are functions not called by any other tracked function.
