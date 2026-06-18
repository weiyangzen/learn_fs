# sources/storage-engines/wiredtiger/tools/gdb/load_gdb_scripts.py

## Purpose
`load_gdb_scripts.py` is the entrypoint that loads WiredTiger's custom GDB debugging helpers. It is designed for manual `source` use and for automatic GDB loading when copied beside a shared library as `<library>-gdb.py`.

## Important APIs and commands
The script imports `gdb`, `sys`, and `os`, prints a loading message, computes `build_dir = os.path.dirname(__file__)`, appends it to `sys.path`, imports `gdb_scripts.hazard_pointers` and `gdb_scripts.dump_insert_list`, and executes `source {build_dir}/gdb_scripts/dump_row_int.gdb` for a Scheme/GDB script.

## Control flow and behavior
Execution is linear. Importing the Python modules registers their GDB command classes at import time. The final `gdb.execute` loads the row-internal-page dump script. There is no error recovery; import or source failures surface directly in GDB.

## State, dependencies, and integration
The loader depends on being located in a directory that also contains `gdb_scripts`, plus copied build-directory packaging when shared-library auto-load is enabled. It integrates with GDB's objfile `-gdb.py` auto-load mechanism and with build steps that copy/rename the loader.

## Risks and test signals
Risks include GDB auto-load safe-path restrictions, missing `gdb_scripts` package files in the build directory, missing `dump_row_int.gdb`, and import-time failures if WiredTiger debug types are unavailable. Signals are the "Loading custom WiredTiger gdb scripts..." message and availability of `dump_hazard_pointers`, `find_hazard_pointers_for`, and `dump_insert_list` commands in GDB.
