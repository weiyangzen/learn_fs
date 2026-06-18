# sources/storage-engines/wiredtiger/tools/hexfiend/Templates/hexparse

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/tools/hexfiend/Templates/hexparse -->
## sources/storage-engines/wiredtiger/tools/hexfiend/Templates/hexparse

### Purpose
`hexparse` is a Tcl command-line compatibility runner for Hex Fiend binary templates. It lets WiredTiger's Hex Fiend templates be executed outside the GUI against one or more binary files, producing textual section/entry output and optional hexdumps. It implements a practical subset of the Hex Fiend template API: endian declarations, integer readers, byte/string readers, sections, entry emission, navigation, includes, and template discovery.

### Important APIs, Types, and Functions
The runtime state is stored in globals: `__f` for the open binary file, `__fs` for file size, `__flag_hexdump` for output mode, indentation buffers, and section accumulator variables. `__args` wraps `cmdline::getoptions`; `__unpack` and `__unpack_entry` read fixed-size binary values with Tcl `binary scan`; integer template functions such as `uint64`, `int32`, `uint16`, and `uint8` delegate to `__unpack_entry`. `bytes`, `ascii`, `str`, and `cstr` provide byte/string readers. `section`, `entry`, `sectionname`, and `sectionvalue` build the displayed parse tree. `goto`, `move`, `pos`, `len`, and `end` expose stream navigation.

### Control Flow
Startup parses hexdump options, computes indentation behavior, resolves the requested template with `__find_template_path`, then loops over each input filename. For each file it prints a header, stores file size, opens the file in binary mode, sources the resolved template, and closes the handle. Template code executes in the interpreter where the compatibility functions are already defined. `section` captures nested output into `__output`, runs its body at caller scope, calculates consumed length by comparing current position with entry position, then flushes at top level.

### State and Persistence
The script does not persist state beyond stdout output. During a file parse, all state is global and reused across template execution; the per-file loop resets `__fs` and `__f` but does not broadly reset every output/control global beyond top-level `section` flushing. `include` reads template support files from `$HOME/Library/Application Support/com.ridiculousfish.HexFiend/Templates`.

### Dependencies and Integration Points
It depends on Tcl, the `cmdline` package, and Hex Fiend template files installed under the macOS application-support path. `install.sh` copies this runner and templates into that location. WiredTiger-specific templates can call this subset of Hex Fiend's Tcl-like API to decode `.wt` files or other binary artifacts.

### Risks and Test Signals
Many Hex Fiend APIs are stubs (`big_endian`, floating-point readers, uuid/date readers, bit readers, hex/utf16, `endsection`) and will fail if templates use them. `cstr` compares against `"\x000"` and may include the terminator in returned data. Template lookup has an apparent bug in ambiguous-name reporting where `file rootname` is called without the candidate path. All file and section state is global, so parser reuse is fragile. Useful tests are small binary fixtures that exercise fixed-width integer parsing, nested sections, `include`, all hexdump modes, EOF handling, and ambiguous/missing template lookup.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/tools/hexfiend/Templates/hexparse -->
