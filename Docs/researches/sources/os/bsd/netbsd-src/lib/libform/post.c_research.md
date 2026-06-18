# File Research: sources/os/bsd/netbsd-src/lib/libform/post.c

Implements public form posting and unposting.

`post_form` validates arguments and state, checks field connection, scales the form against the target window, runs form and field init hooks, positions the first field, draws the current page, marks the form posted, and positions the cursor.

`unpost_form` checks state, runs field and form termination hooks, clears the form window, and clears the posted flag.

Behavior is tightly coupled to `internals.c` for first-field positioning and page drawing.
