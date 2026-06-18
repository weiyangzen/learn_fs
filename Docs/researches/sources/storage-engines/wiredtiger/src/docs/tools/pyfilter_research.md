# sources/storage-engines/wiredtiger/src/docs/tools/pyfilter

## Purpose
Shell wrapper for Python documentation filtering.

## APIs and control flow
The script computes its own directory and runs `python $tooldir/doxypy.py "$@" | python $tooldir/fixlinks.py`. It first converts Python docstrings into Doxygen-style comments, then rewrites links and C API references.

## State, dependencies, integration, risks
The wrapper has no durable state. It depends on `/bin/sh`, `python`, the two sibling Python scripts, and pipe behavior. It integrates with Doxygen as an input filter for Python sources. Risks are losing the upstream `doxypy.py` exit status through the pipeline in plain `sh`, Python version ambiguity, and path quoting limitations. Test signals are executable permissions, successful transformation of a sample Python binding file, and failure behavior when either Python script is missing.
