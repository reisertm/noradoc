# System Backend

This chapter documents the system control layer exposed by `dpxcontrol`, which is also available through:

```bash
nora --admin
```

In practice, `nora --admin ...` forwards directly to `dpxcontrol`. This layer is different from the project-oriented `nora` CLI described in [Administration Backend](administration-backend.md): it controls services, Docker, daemon processes, DICOM listeners, database maintenance, and system tests for a NORA installation.

## Role of `dpxcontrol`

`dpxcontrol` is the system manager for a NORA instance. It is responsible for operational tasks such as:

- starting and stopping the backend stack
- checking service status
- managing the daemon
- managing DICOM `storescp` listener nodes
- managing the optional Docker runtime
- launching MATLAB with `DPX_startup`
- running database maintenance commands
- cleaning transient folders
- running infrastructure tests

Before doing any work, the script loads the instance configuration from `conf/*.conf`. If no config is present, it aborts and asks for `bin/setup_config`.

## Basic usage

Top-level usage follows this pattern:

```bash
dpxcontrol <command> [subcommand] [options]
```

Equivalent through the main CLI:

```bash
nora --admin <command> [subcommand] [options]
```

Examples:

```bash
dpxcontrol status
nora --admin daemon restart --nodejs
nora --admin docker logs
```

## Main service commands

The simplest entry points operate on the full stack:

- `dpxcontrol start`
- `dpxcontrol stop`
- `dpxcontrol restart`
- `dpxcontrol status`

These expand internally to the grouped modules:

- `docker`
- `storescp`
- `daemon`
- `xvfb`

There is also an explicit form:

```bash
dpxcontrol all start
dpxcontrol all status
```

### Important runtime checks

The script applies a few safeguards:

- start/stop is blocked from inside the Docker container host `noradocker`
- starting most modules as `root` is blocked, except the daemon path
- autostart flags in the config can suppress module actions for `all start`

## Component-specific control

You can control individual subsystems directly.

### Docker

```bash
dpxcontrol docker start
dpxcontrol docker stop
dpxcontrol docker restart
dpxcontrol docker status
dpxcontrol docker logs
```

Additional Docker helper commands:

```bash
dpxcontrol docker build
dpxcontrol docker bash
dpxcontrol docker bash '<command>'
dpxcontrol docker setup
dpxcontrol docker fwall allow
dpxcontrol docker fwall deny
```

What these do:

- `build`
  Builds the Docker image for the instance.
- `start`
  Starts the configured container, removing stale containers with the same instance name if needed.
- `stop`
  Stops and removes the running container.
- `status`
  Shows whether the instance container is running.
- `logs`
  Prints container logs.
- `bash`
  Opens an interactive shell inside the container.
- `bash '<command>'`
  Runs one command inside the container.
- `setup`
  Runs `/dpx/docker/setupdocker` inside the container.
- `fwall allow|deny`
  Adjusts Docker forwarding firewall rules with `iptables`.

Notes:

- Docker commands require either Docker group membership or a rootless Docker setup via `DOCKER_HOST`.
- When no Docker subcommand is given, `dpxcontrol` prints a Docker-specific help summary.
- The image name is instance-specific and derived from the installation path.

### Daemon

```bash
dpxcontrol daemon start
dpxcontrol daemon stop
dpxcontrol daemon restart
dpxcontrol daemon status
```

The daemon can be launched in several modes:

- `--matlab`
- `--octave`
- `--nodejs`
- `--nodemon`

Examples:

```bash
dpxcontrol daemon start --matlab
dpxcontrol daemon restart --octave
dpxcontrol daemon start --nodejs
dpxcontrol daemon start --nodemon
```

Behavior:

- MATLAB mode starts `DPX_demon` through `DPX_startup`
- Octave mode does the same through the configured Octave binary
- Node.js mode starts `src/node/DPX_demon.js`
- Nodemon mode starts the same Node daemon with file watching

Operational details:

- the daemon log is written to `var/syslogs/daemon.log`
- in Docker mode the daemon may run inside the container
- on some host-grid setups, `sudo` may be required to manage the daemon
- `status` checks for the daemon's unique process tag

### DICOM `storescp` listener nodes

```bash
dpxcontrol storescp start
dpxcontrol storescp stop
dpxcontrol storescp restart
dpxcontrol storescp status
```

This controls the configured inbound DICOM listener nodes. The script iterates over the configured `storescp` entries from the config and starts one `storescp` process per node.

Per-node behavior includes:

- reading the configured `port`
- reading optional `timeout`
- reading optional `outputdirectory`
- reading optional `deleteafterimport`
- reading optional `type`
- applying the PACS naming scheme

The listener can trigger post-end-of-study import handling through:

- `htdocs/dicom/storescp_helper.php`

Notes:

- if a node is already running, `start` reports the PID and port
- `restart` is implemented as stop followed by start
- `status` reports per-node running state
- in Docker mode the listeners may run in the container instead of on the host

### Xvfb

```bash
dpxcontrol xvfb start
dpxcontrol xvfb stop
dpxcontrol xvfb restart
dpxcontrol xvfb status
```

This controls the virtual X server used by parts of the backend stack that need a display.

Behavior:

- uses `Xvfb :$XVFB_DISPLAY_ID`
- checks for an existing tagged Xvfb process
- refuses to start when the display is already locked by a different process

Special case:

- for `all stop` and `all restart`, Xvfb stop is intentionally skipped unless you call the `xvfb` module directly

## MATLAB command

There is a dedicated MATLAB control entry:

```bash
dpxcontrol matlab
```

This starts MATLAB and runs `DPX_startup`.

Additional mode:

```bash
dpxcontrol matlab updatedb
```

This starts MATLAB and runs:

- `DPX_SQL_updateRootTables()`
- `DPX_SQL_updateProject('<all>')`

This is used to refresh root tables and project metadata structures.

In Docker mode, MATLAB is launched inside the container.

## MySQL and database maintenance

Database administration commands are grouped under `mysql`.

### Backups

```bash
dpxcontrol mysql backup
dpxcontrol mysql backup <project>
dpxcontrol mysql backup _nosys_
```

Behavior:

- `backup`
  Backs up the full database set.
- `backup <project>`
  Backs up one project database only.
- `backup _nosys_`
  Backs up NORA content without system tables, useful for some migrations.

### Restore

```bash
dpxcontrol mysql restore
dpxcontrol mysql restore <linenumber>
```

Behavior:

- `restore` without a line number shows available backups
- `restore <linenumber>` performs the selected restore

This is intentionally guarded because it can wipe the current database content.

### Schema and initialization commands

```bash
dpxcontrol mysql reset
dpxcontrol mysql update <project>
dpxcontrol mysql export-defaults
```

Behavior:

- `reset`
  Reinitializes the database and deletes all content.
- `update <project>`
  Updates database structures. The help text explicitly mentions using `--all`, `DPX`, or a project name.
- `export-defaults`
  Exports default table structures. The script labels this as a superadmin task.

Implementation notes:

- these commands are dispatched to scripts such as `/dpx/docker/setupmysql`, `/dpx/docker/updatemysql`, and `htdocs/backup.php`
- they are primarily designed to run through the Docker environment

## Cleanup

```bash
dpxcontrol clean
```

This removes transient content from the local `var` tree:

- `var/logs/`
- `var/export/`
- `var/tmp/`

This is filesystem cleanup only. It does not perform database cleanup.

## Tests

Infrastructure tests are grouped under `test`.

```bash
dpxcontrol test email
dpxcontrol test slurm
dpxcontrol test storescp
dpxcontrol test frontend
dpxcontrol test frontend live
```

Behavior:

- `test email`
  Sends a test email to configured admins.
- `test slurm`
  Runs a minimal `srun` command through the Docker environment.
- `test storescp`
  Sends a test DICOM file to the local `storescp` listener.
- `test frontend`
  Runs mocked frontend integration tests.
- `test frontend live`
  Runs frontend tests against a live server connection.

## Version increment

There is also a simple version helper:

```bash
dpxcontrol incver
```

This updates `conf/version.conf` and then runs `reconfigure`.

## Debugging options

Several commands support:

```bash
--debug
```

In debug mode, the script prints the command it would run and avoids backgrounding it, which is useful for diagnosing failing daemon, Xvfb, or `storescp` starts.

Examples:

```bash
dpxcontrol daemon start --nodejs --debug
dpxcontrol storescp start --debug
dpxcontrol xvfb start --debug
```

## Relation to other documentation

Use this chapter when you are operating a NORA installation itself.

Use [Administration Backend](administration-backend.md) when you want the project-level CLI for:

- file selection
- tagging
- import
- job launch
- metadata export

Use [Installation](nora-inside-a-docker.md) when you need the broader deployment workflow around Docker setup and instance configuration.
