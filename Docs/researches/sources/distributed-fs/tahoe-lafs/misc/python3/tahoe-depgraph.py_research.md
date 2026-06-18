# sources/distributed-fs/tahoe-lafs/misc/python3/tahoe-depgraph.py

## Purpose

This script generates JSON data describing internal `allmydata` module dependencies and Python 3 porting status.

## Important APIs, Types, and Functions

`mymf` subclasses `modulefinder.ModuleFinder`, recording `_depgraph`, `_types`, and `_last_caller`. It overrides `import_hook`, `import_module`, and `load_module` to capture imports between `allmydata` modules and module load types while skipping names ending `_py3`. `as_json` returns serializable dependency/type maps. `main(target)` discovers modules under `src/allmydata`, imports them via a temporary script, writes `tahoe-deps.json`, executes `_python3.py` to read port lists, and writes `tahoe-ported.json`.

## Control Flow

The walker excludes `test` directories, `setup.py`, and filenames containing hyphens. It uses Twisted `reflect.filenameToModuleName` to convert paths. The temporary script imports all discovered modules, causing modulefinder callbacks to populate the graph. Output JSON is sorted and indented.

## State, Dependencies, Integration, Risks, and Tests

Persistent state is `tahoe-deps.json` and `tahoe-ported.json` in the current directory. Dependencies are stdlib `modulefinder`, Twisted reflect, and executable Tahoe source. Integration is `depgraph.sh` publishing. Risks include executing `_python3.py` with `exec`, import side effects during analysis, old `modulefinder` APIs, skipped tests, and load-type values that may not be JSON-stable across Python versions. Tests should use a tiny package tree, assert dependency edges, skip behavior, and port-status extraction.
