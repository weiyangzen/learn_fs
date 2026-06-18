# sources/test-tools/fio/ghelpers.h

Purpose: header for gfio GTK helper widgets and small display utilities.

Important APIs/types/functions: declares framed widget factories, integer label/entry setters, scrolled-window creation, `struct multitext_widget`, multitext management functions, tree-view alignment/visibility/sort flags, and `tree_view_column`.

Control flow: callers include this header to build consistent gfio pages and result tables without duplicating GTK boilerplate.

State and persistence behavior: exposes the `multitext_widget` state layout: entry widget, dynamic text array, current index, and maximum index/count. Other functions operate on caller-owned GTK widgets.

Dependencies/integration: requires GTK types from including context or GTK headers included elsewhere. Included by `gfio.h` and GUI implementation files.

Risks and test signals: callers must initialize `multitext_widget` storage to zero before use and must not update out-of-range indexes. Compile and UI smoke tests cover this header.
