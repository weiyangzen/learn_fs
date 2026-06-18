# sources/storage-engines/foundationdb/documentation/sphinx/extensions/relativelink.py

## Purpose
This Sphinx extension monkey-patches toctree resolution so toctree entries can contain relative internal links using `relative://path`, later emitted as plain relative `href` values.

## Important APIs, Types, And Functions
`setup(app)` imports `sphinx.environment.adapters.toctree` and `docutils.nodes`, saves `TocTree.resolve` as `old_resolve`, defines `resolve_toctree`, and replaces `TocTree.resolve`. The wrapper traverses resolved reference nodes and rewrites non-internal `refuri` values that start with `relative://`.

## Control Flow
During Sphinx toctree resolution, the patched method calls the original resolver, returns `None` unchanged, then mutates reference nodes in the resolved tree. The wrapper signature mirrors the Sphinx method signature but calls `old_resolve` with hard-coded values rather than forwarding the incoming `prune`, `maxdepth`, `titles_only`, `collapse`, and `includehidden` arguments.

## State And Persistence
It mutates the process-global Sphinx `TocTree.resolve` function for the duration of the Sphinx process. No files are persisted by the extension itself.

## Dependencies And Integration Points
It depends on Sphinx's internal `environment.adapters.toctree.TocTree` API and docutils reference node shape. It is loaded by `conf.py` and affects docs source files that use `relative://` in toctrees.

## Risks
Monkey-patching internal Sphinx APIs is version-sensitive. The wrapper currently ignores the caller's toctree-resolution arguments and always passes `prune=True`, `maxdepth=0`, `titles_only=False`, `collapse=False`, and `includehidden=False`, which can alter behavior outside relative-link rewriting. It also uses `result == None` rather than identity comparison.

## Test Signals
A docs build with a toctree entry like `Name <relative://some/path>` should render a relative href. Regression tests should also verify hidden/collapsed/maxdepth toctree behavior is not changed unintentionally by the hard-coded forwarding.
