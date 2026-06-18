# File Research: sources/os/plan9/plan9/sys/src/cmd/dict/robert.c

Implements callbacks for Robert Électronique dictionaries, including main index entries and verb-form entries.

The backend uses binary pointer/index records. `robertindexentry` decodes offsets and lengths for etymology and definition data from the index entry, opens `defs.rob` and `etym.rob` lazily through `Bouvrir`, reads those slices into `Entry` objects, then calls the internal `robertprintentry`.

`intab` maps the source character set and embedded control bytes to Unicode runes or internal controls: citation pointer, font changes, superscript/subscript state, and ignored style markers. `suptab` and `subtab` map ASCII digits/operators to super/subscript runes.

`robertprintentry` emits definition text, handles newlines/line counting, injects etymology after the first definition line when available, follows citation controls into `cits.rob`, and applies one-character superscript/subscript conversions. Style controls are mostly ignored unless debug is enabled. `citation` reads one citation record ending at byte `0xc8` and recursively prints it.

`robertnextoff` advances fixed 16-byte pointer records. `robertprintkey` dumps `/lib/dict/robert/_phon`. `robertflexentry` handles verb forms from `flex.rob`, turning `$` into line breaks and limiting headword output to the second line. `robertnextflex` advances to the next `$`.

Integration points: registered in `utils.c` as `robert` and `robertv`.

Risks and notes: opens hard-coded auxiliary files, exits on open failure, and assumes binary record layouts exactly. Citation recursion and pointer data rely on trusted dictionary files. Many style/font controls are discarded.
