# Jupyter, VS Code Server, and OpenSSH Setup

This chapter is a practical setup tutorial for the three interactive development services currently supported by NORA:

- Jupyter Lab
- code-server / VS Code in the browser
- per-user OpenSSH access

## Before you start

All three services are launched as NORA jobs. So before configuring them, make sure:

1. your NORA instance can already submit jobs
2. the queue you want to use is visible in NORA
3. the target compute nodes can see the same filesystem paths as NORA
4. your `main.conf` jail and environment settings do not hide the required binaries or folders

In practice, these services depend especially on:

- queue settings in `main.conf`
- the shell environment used on the worker nodes

## How interactive services work in NORA

The common pattern is:

1. a user starts Jupyter, code-server, or OpenSSH from the frontend
2. `KCommandDialog.js` creates a generic BASH job
3. placeholders like `$NOTEBOOKDIR` or `$INITPWD` are substituted
4. the job is submitted to the selected queue
5. the service prints its connection information into the job log
6. the frontend reads that log and opens the URL or shows the SSH command

So the setup task is mainly:

- provide a working config snippet
- make sure the referenced binaries and folders exist on the worker nodes

## Tutorial 1: Set up Jupyter Lab

### Minimal working config

Create `conf/jupyter.conf` with a minimal version like this:

```js
{
"jupyter" : {
      "call":"IPaddr=$(hostname -I  | cut -d\" \" -f1); \
              . /path/to/environment-setup.sh; \
              jupyter lab --ip $IPaddr --no-browser --notebook-dir=$NOTEBOOKDIR --NotebookApp.terminado_settings='{\"shell_command\":[\"/bin/bash\",\"-lc\",\". /path/to/environment-setup.sh; exec /bin/bash -i\"]}'",
      "notebookdir":"/shared/notebooks",
      "readme":"/shared/docs/readme_cluster.txt",
      "homedir":"/home/serviceuser",
      "kspec" : {
        "python": {
                       "display_name": "jupyter",
                       "language": "python",
                       "name": "juypter"
                  },
            "matlab": {
                       "display_name": "Matlab",
                       "language": "matlab",
                       "name": "matlab"
              },
            "bash" :  {
                       "display_name": "Bash",
                       "language": "bash",
                       "name": "bash"
                  }
         }
}
}
```

For the `terminado_settings` shell startup, replace the same environment hook with your local one, for example:

```text
\"shell_command\":[\"/bin/bash\",\"-lc\",\". /path/to/environment-setup.sh; exec /bin/bash -i\"]
```

If you want the simplest possible start, the essential parts are just:

- `call`
- `notebookdir`

The rest is convenience.

### What this config does

- creates an IPython startup directory
- disables `get_ipython().system` in the notebook startup hook
- loads your worker-node software environment
- starts `jupyter lab` on the node IP
- uses `$NOTEBOOKDIR` as the notebook root
- configures notebook terminals to start a prepared Bash shell

### Required prerequisites

Make sure the worker nodes have:

- `jupyter lab`
- a shell setup command that makes `jupyter` available
- write access to the notebook directory root such as `/shared/notebooks`

### Important path choice

The current setup uses:

```js
"notebookdir":"/shared/notebooks"
```

NORA will create a user-specific subfolder there and bind it as the effective home directory for the interactive job.

That means this directory should be:

- persistent
- writable
- shared across the nodes where users may start notebooks

### Test it

1. restart or reload the instance if needed so the config is visible
2. open NORA
3. start a Jupyter job from the Jupyter dialog
4. choose a queue that allows interactive jobs
5. wait for the log to print the notebook URL

If it fails, first test the core command manually on a worker node:

```bash
. /path/to/environment-setup.sh
which jupyter
```

### Minimal troubleshooting

- If the notebook starts but no files are visible, the notebook directory or jail bindings are wrong.
- If the job starts but no URL appears, the Jupyter command failed before startup.
- If terminals inside Jupyter behave differently than expected, check the `terminado_settings` shell command.

## Tutorial 2: Set up code-server / VS Code

### Minimal working config

Create `conf/codeserver.conf` like this:

```js
{
"codeserver" : {
        "call":"port=$(for port in {8080..8090}; do ! ss -ltn | awk '{print $4}' | grep -q \":$port\$\" && echo $port && break; done);\
                pwd=$INITPWD;\
                cfg=$NOTEBOOKDIR/.config/code-server;\
                . /path/to/environment-setup.sh;\
                if [ -z $(readlink $NOTEBOOKDIR/.local) ]; then ln -s /home/$USER/.local $NOTEBOOKDIR/.local; fi;\
                mkdir -p $cfg;\
                cfgfile=$cfg/config.yaml;\
                if [ -f $cfgfile ]; then echo cfg found; else\
                    TXT=\"Your initial password is $INITPWD\"; echo \"auth: password\npassword: $pwd\ncert: false\n\" > $cfgfile; fi;\
                IPaddr=$(hostname -I  | cut -d\" \" -f1);\
                echo link:https://<your-nora-host>/${IPaddr//./-}_$port>&2;\
                /path/to/code-server --disable-workspace-trust --bind-addr 0.0.0.0:$port --config $cfgfile --user-data-dir $NOTEBOOKDIR $NOTEBOOKDIR --abs-proxy-base-path /${IPaddr//./-}_$port/",
      "notebookdir":"/shared/notebooks",
      "notebookdir_debug":"/shared/notebooks/debug"
}
}
```

Again, the essential keys are:

- `call`
- `notebookdir`

### What this config does

- finds a free port in `8080..8090`
- uses `$NOTEBOOKDIR` as persistent user workspace
- writes a `code-server` config on first start
- uses `$INITPWD` as initial password
- prints the browser URL to stderr as `link:...`
- starts your `code-server` binary

The placeholders are filled by the launcher:

- `$NOTEBOOKDIR` becomes the user root directory
- `$INITPWD` becomes `<username>@nora`

### Required prerequisites

Make sure the worker nodes have:

- a `code-server` binary
- a shell setup command that makes `code-server` available, if needed
- a writable notebook directory root

### The one setup step that usually breaks

The current config assumes a reverse proxy and prints URLs like:

```text
https://<your-nora-host>/<node-ip-with-dashes>_<port>
```

This only works if your web frontend or reverse proxy forwards paths of the form:

```text
/<node-ip-with-dashes>_<port>/
```

to the matching node and port.

So the minimal working setup for code-server is not only the config file. You also need the proxy rule.

### Test it

1. create `conf/codeserver.conf`
2. start code-server from the frontend
3. wait for the job log to print a `link:...`
4. open the link

If the job runs but the link does not work:

- the proxy setup is wrong
- or `code-server` is listening on a different address or path than expected

### Minimal troubleshooting

- If the log never prints `link:`, the start command failed.
- If the link opens but shows a bad gateway, the proxy route is wrong.
- If code-server starts but extensions or settings are not persistent, the notebook directory is not correctly mounted or writable.

## Tutorial 3: Set up per-user OpenSSH access

### Minimal working config

Create `conf/openssh.conf` with:

```js
{
  "openssh":{
    OPENSSH_FORCE_COMMAND: "/bin/bash -lc 'if [ -f /path/to/conda.sh ]; then . /path/to/conda.sh >/dev/null 2>&1; conda activate base >/dev/null 2>&1; fi; if [ -n \"$SSH_ORIGINAL_COMMAND\" ]; then exec /bin/bash -lc \"$SSH_ORIGINAL_COMMAND\"; else exec /bin/bash -l; fi'"
  }
}
```

If you want the absolute minimal version, you can also start with:

```js
{
  "openssh":{
    OPENSSH_FORCE_COMMAND: ""
  }
}
```

That disables custom shell initialization and leaves only the generated default wrapper behavior.

### What this config does

The recommended example:

- loads your shell or Conda setup if it exists
- activates the `base` environment
- executes `SSH_ORIGINAL_COMMAND` when the client sent one
- otherwise opens a login shell

This is useful because the SSH server launched by NORA is job-local and should usually expose the same prepared environment as the interactive compute session.

### What `runsshd.sh` does for you

NORA does not expect a system-wide SSH daemon setup for this feature. Instead it launches a per-user SSH daemon with:

- a private config under `~/.sshd`
- generated host keys
- the submitted public key in `authorized_keys`
- an automatically selected free port starting at `2222`
- environment snapshotting into a per-instance env file
- the configured `OPENSSH_FORCE_COMMAND` injected as `ForceCommand`

So the minimal setup task is mostly making sure the required binaries exist.

### Required prerequisites

Make sure the worker nodes have:

- `/usr/sbin/sshd`
- `ssh-keygen`
- a firewall/network setup that allows connecting to the chosen port from the intended client side

### Test it

1. create `conf/openssh.conf`
2. open the OpenSSH launch dialog in NORA
3. paste a public SSH key
4. optionally enter a port, otherwise let NORA choose one
5. launch the job
6. wait for the job log to print:

```text
Connect with:
ssh -p <port> <user>@<host>
```

7. connect using that SSH command

### Minimal troubleshooting

- If the job fails immediately, `sshd` is probably missing or not executable.
- If the job starts but login shells are wrong, the `OPENSSH_FORCE_COMMAND` is broken.
- If the SSH command is shown but the connection fails, the node or port is not reachable from the client.

## What NORA does automatically

It helps to know which parts you do not need to configure manually.

### Frontend launcher

`KCommandDialog.js` already knows how to:

- build the Jupyter job
- build the code-server job
- build the OpenSSH job
- watch the logs for the connection information

You do not need to patch frontend code for a normal setup if your config files follow the current pattern.

### Per-user notebook homes

`DPX_core.js` already creates and binds user notebook folders below:

```text
<jupyter.notebookdir>/<username>
```

and uses that as the effective interactive home directory. This is why Jupyter and code-server can share the same persistent workspace root.

## Recommended minimal rollout

If you want the fastest path to a working setup:

1. Set up Jupyter first.
2. Reuse the same notebook root for code-server.
3. Add OpenSSH only after the job and network model are confirmed to work.

That order is practical because:

- Jupyter has the fewest external dependencies
- code-server adds reverse-proxy requirements
- OpenSSH adds client connectivity and shell-environment concerns

## Common pitfalls

- notebook root exists but is not writable by the run user
- `jupyter lab` or `code-server` is installed on the web node but not on the compute nodes
- reverse proxy is missing for code-server
- `OPENSSH_FORCE_COMMAND` is copied with broken quoting
- the selected queue does not support the intended interactive runtime
- jail settings hide required paths

## Relation to other documentation

Use [Jupyter Notebooks](jupyter-notebooks.md) for user-facing notebook usage.

Use [Jobs](jobs.md) for the generic job model behind these launches.

Use [Configuration Files](configuration-files.md) for the broader config overview.

Use [System Backend](system-backend.md) if you need service-level system administration rather than interactive job setup.
