# sources/storage-engines/wiredtiger/src/docs/style/DoxygenLayout.11.xml

## Purpose
Doxygen layout definition for newer Doxygen navigation and page structure, likely Doxygen 1.11-era output.

## Structure and integration
The XML declares nav tabs for main page, pages, topics titled `Modules`, namespaces, classes, files, examples, and user tabs for Community and License. It defines class, namespace, file, group, and directory page sections, controlling visibility for descriptions, include graphs, member declarations, member definitions, author sections, and directory graphs. Variables such as `$ALPHABETICAL_INDEX`, `$SHOW_INCLUDE_FILES`, `$CLASS_GRAPH`, `$COLLABORATION_GRAPH`, `$INCLUDE_GRAPH`, `$INCLUDED_BY_GRAPH`, `$GROUP_GRAPHS`, and `$SHOW_USED_FILES` defer behavior to Doxygen config.

## State, dependencies, risks, tests
The file is declarative and has no runtime state. It depends on Doxygen accepting `version="1.0"` layout syntax and the `topics` tab type. Risks are schema drift between Doxygen versions, accidental visibility changes, and divergence from the non-`.11` layout. Test signals are successful Doxygen generation with expected nav tabs and no layout warnings.
