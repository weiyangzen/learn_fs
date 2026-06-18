## sources/storage-engines/pebble/tool/make_lsm_data.sh

Purpose: generation script for `lsm_data.go`, embedding the LSM viewer CSS and JavaScript into Go raw string variables.

Important APIs/functions: shell variables `dest`, `do`, `not`, and `edit` build the generated header without spelling the generated-file sentinel directly in one token. The script writes Go package header, starts `lsmDataCSS`, appends `data/lsm.css`, starts `lsmDataJS`, appends `data/lsm.js`, and closes the raw string.

Control flow: sequential `cat >`, `cat >>`, and heredoc operations create the generated file in the current directory. It is referenced by `//go:generate ./make_lsm_data.sh` in `lsm.go`.

State and persistence: overwrites `lsm_data.go`. It reads from `tool/data/lsm.css` and `tool/data/lsm.js` relative to the current working directory expected by `go generate`.

Dependencies and integration: relies on POSIX shell, `cat`, and the asset files. `lsm.go` consumes the generated variables for embedded HTML output.

Risks: raw string embedding will break if CSS or JS contains a backtick. Running the script from the wrong directory will fail or create an incorrectly located file. It does not include D3 itself; the HTML still references D3 separately.

Test signals: no direct test. Compilation of `lsm.go` ensures `lsmDataCSS` and `lsmDataJS` exist after generation.
