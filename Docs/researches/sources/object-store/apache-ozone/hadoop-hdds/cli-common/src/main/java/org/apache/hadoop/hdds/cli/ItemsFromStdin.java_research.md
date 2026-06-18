# sources/object-store/apache-ozone/hadoop-hdds/cli-common/src/main/java/org/apache/hadoop/hdds/cli/ItemsFromStdin.java

Purpose: Abstract helper for CLI parameters that accept a list of items either from command-line arguments or from standard input when the first argument is `-`.

Important APIs/types/functions: `FORMAT_DESCRIPTION` provides reusable option help suffix text. `setItems(List<String>)` is the main mutator. `isReadFromStdin()`, `getItems()`, `iterator()`, and `size()` expose the loaded items. `readItemsFromStdin()` reads UTF-8 lines with `Scanner` and trims each line.

Control flow: Subclasses call `setItems` from picocli setter methods. If the argument list starts with `-`, all items are replaced by lines read from stdin; otherwise the supplied list or an empty list is stored.

State and persistence behavior: Holds an in-memory item list and a boolean indicating stdin mode. `getItems()` returns an unmodifiable view.

Dependencies and integration points: Used by CLI commands needing repeated item arguments. Depends on Jakarta `@Nonnull`, standard input, and Java collection iteration.

Risks: Reading stdin is blocking until EOF, so commands must document usage. Only the first argument controls stdin mode; later arguments are ignored in stdin mode. Trimming lines may remove significant whitespace.

Test signals: Tests should cover null/empty arguments, normal lists, `-` stdin mode with multiple lines, iterator behavior, and unmodifiable output.
