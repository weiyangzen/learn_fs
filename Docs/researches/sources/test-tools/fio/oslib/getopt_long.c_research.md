# sources/test-tools/fio/oslib/getopt_long.c

Purpose: klibc-derived fallback implementation of a common subset of `getopt_long_only()`.

Important APIs/functions: defines globals `optarg`, `optind`, `opterr`, and `optopt`; internal `option_matches()` checks exact or unique prefix long-option matches; `getopt_long_only()` parses long `--name[=arg]` options and short `-x` clusters with required/optional arguments.

Control flow and state: private static `pvt` remembers the current character pointer, previous `optstring`, and previous `argv` to reset parsing when a different parse begins. Long option parsing increments `optind`, finds exact or unique short matches, handles `flag` vs `val`, and populates `longindex`. Short option parsing advances within a cluster and handles missing arguments with `:` or `?`.

Dependencies and integration: includes the fallback `getopt.h`; consumed by fio CLI setup on platforms lacking native support.

Risks: documented limitations include no option reordering, no `-W foo`, and no special first `optstring` character `-`. Globals are process-wide and not thread-safe. Ambiguous long prefixes return `?`.

Test signals: parse exact long options, unique/ambiguous abbreviations, `--`, missing required arguments, optional arguments, short clusters, and repeated parses with different `argv`.
