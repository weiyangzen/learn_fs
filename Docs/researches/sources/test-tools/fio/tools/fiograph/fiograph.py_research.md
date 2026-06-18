# sources/test-tools/fio/tools/fiograph/fiograph.py

## Purpose
`fiograph.py` renders fio job files into Graphviz diagrams showing jobs, execution groups, selected options, dependencies, runtime/size self-loops, and a legend.

## Important APIs, Types, and Functions
Config accessors (`get_section_option`, `get_config_option`, color/style getters, `get_specific_options`) mediate fio and visualization config. `render_option()` appends option rows unless the option is skipped or already represented graphically. `render_options()` builds each job node's HTML label, handling `numjobs`, early options, ioengine-specific options, generic sorted options, and late options. `render_section()` adds a node plus runtime or size self-loop. `create_sub_graph()` creates clustered execution groups. `create_legend()` builds a Graphviz legend. `fio_to_graphviz()` parses a fio file and constructs the full graph. `setup_commandline()` and `main()` handle CLI and output file movement.

## Control Flow and State
Globals `config_file` and `fio_file` hold parsed config. `main()` resolves config path, renders to a UUID temporary filename, renames the image to the requested/default output, and optionally preserves the `.gv` source. Job dependencies are inferred from `stonewall`, `wait_for_previous`, and `wait_for`, with clusters representing groups of parallel jobs.

## Dependencies and Integration Points
It depends on Python `graphviz`, Graphviz `dot`, `configparser`, fio job-file INI syntax, and `fiograph.conf`. It uses `RawConfigParser` with `default_section="global"` for fio files.

## Risks and Test Signals
Risks include a Python logic bug where `('stonewall' or 'wait_for_previous') in section` only checks `stonewall`, HTML label injection from unescaped option values, dependency references to missing jobs, and output rename failures. Signals are generated image files, optional `.gv` content, and Graphviz/render exceptions.
