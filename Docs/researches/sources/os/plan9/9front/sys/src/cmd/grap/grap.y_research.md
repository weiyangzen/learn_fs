# File Research: sources/os/plan9/9front/sys/src/cmd/grap/grap.y

Yacc grammar for `grap` input inside `.G1/.G2`. It recognizes graph blocks, frame/ticks/grid/label/coord/plot/line/circle/draw/next/copy/for/if/print statements, numeric lists, strings with size/justification attributes, points, coordinate declarations, and arithmetic/logical expressions.

Parser actions directly call the implementation functions in the C files. Expressions include arithmetic, comparisons, boolean operators, math functions, random, max/min/int, variable assignment, and string equality tests. The grammar drives code generation state so empty or erroneous graphs do not emit pic output.
