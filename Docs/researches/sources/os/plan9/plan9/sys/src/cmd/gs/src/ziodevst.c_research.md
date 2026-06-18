# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/ziodevst.c

`%static%` IODevice implementation for serving embedded initialization/resource data from `gs_init_string`. It defines a GC-managed `iostatic_state` holding a PostScript dictionary of static file metadata.

`iostatic_init` allocates and installs the state object. `iostatic_open_file` expects file names of the form `/category/instance`, looks up that category and instance in the configured dictionary, reads `StaticFilePos` and `StaticFileEnd`, and returns a read stream over the corresponding byte range in `gs_init_string`. Missing or malformed metadata returns `undefinedfilename` or `unregistered` depending on the failure.

`.setup_io_static` installs the dictionary into the `%static%` IODevice state with a write barrier. The GC mark/enumerate/relocate procedures ensure the stored dictionary reference is traced and relocated correctly.
