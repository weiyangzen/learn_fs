# sources/storage-engines/wiredtiger/test/format/format_disagg_multi.sh

## Purpose
`format_disagg_multi.sh` is an interactive tmux harness for running format in multi-node disaggregated mode and watching leader/follower logs side by side.

## Important APIs, Types, And Functions
The script defines `msg`, `fatal_msg`, `onintr`, and `usage`. It parses `-h/--home`, `-c/--config`, `-v/--validation`, `-r/--rows`, and `-o/--ops`. It uses `tmux`, `tput`, `tail -F`, and the local `./t` binary.

## Control Flow
The script selects either a custom config or defaults to `../../../test/format/CONFIG.disagg` plus injected settings `disagg.multi=1`, `runs.predictable_replay=1`, validation flag, row range, and operation range. It kills any prior tmux session with the fixed session name, starts a run window executing `./t`, opens a logs window, tails `leader.out`, splits a second pane for `follower/follower.out`, configures pane titles/layout/mouse/status, then attaches.

## State And Persistence Behavior
The harness does not modify source files. It causes the format binary to create or reuse the selected run home and logs under `leader.out` and `follower/follower.out`. It owns tmux session state named `format_disagg_multi_node`.

## Dependencies And Integration Points
It assumes it is run from a build directory with `./t`, that `tmux` and terminal color capabilities exist, and that the C disaggregated setup will create the expected log files. It complements `format_disagg.c` by making manual multi-node runs observable.

## Risks And Test Signals
Risks include fixed tmux session-name collision, indefinite waits for log files if startup fails before log creation, color setup failures in noninteractive terminals, and quoting limitations in the constructed tmux command. Signals are live leader/follower log panes and the underlying format program exit shown in the run pane.
