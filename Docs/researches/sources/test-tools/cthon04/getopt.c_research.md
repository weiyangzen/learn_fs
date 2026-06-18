# sources/test-tools/cthon04/getopt.c

Purpose: bundled public-domain getopt implementation plus a standalone command that rewrites shell arguments in a canonical getopt output form.

Important APIs/types/functions: global getopt variables opterr, optind, optopt, optarg; function nfs_getopt(argc, argv, opts); main() wrapper. Uses ERR macro with write(), strchr()/index(), strcmp(), sprintf(), strcat(), and printf().

Control flow: nfs_getopt tracks position within grouped option strings using static sp, returns EOF at end or --, emits '?' for illegal/missing options, and sets optarg for options followed by ':' in the option spec. main() treats argv[1] as the legal option spec, calls nfs_getopt over argv[1..], builds a line containing parsed options, `--`, and remaining operands, then prints it.

State and persistence behavior: no file persistence; parsing state lives in global/static variables and is not reentrant.

Dependencies and integration points: supplied for systems lacking getopt or for harness scripts that expect the historical command-line utility behavior.

Risks: fixed BUFSIZ buffers can overflow with long argument lists; old implicit declarations for write/exit on some platforms; global state prevents concurrent independent parses.

Test signals: exit 0 with a canonical option line, exit 2 on usage or parse error.
