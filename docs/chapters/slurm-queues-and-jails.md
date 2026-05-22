# Slurm, NORA Queues, and Job Jails

This chapter explains three related topics:

- how NORA submits jobs to Slurm
- what a NORA queue is
- how the sandbox or jail layer works and how to configure it

The relevant config files are:

- `conf/main.conf`
- `conf/slurm.conf`
- `conf/jail.conf`

## Basic idea

NORA itself does not execute most processing jobs directly in the web process. Instead, it generates job scripts and submits them to a scheduler.

In a Slurm-based setup, the flow is:

1. a user launches a job from the viewer, batch tool, notebook dialog, or backend
2. NORA chooses a queue name
3. NORA resolves that queue name into a scheduler type and optional Slurm parameters
4. NORA submits the job via `sbatch`
5. optionally, NORA wraps the job inside a filesystem jail before execution

So there are two separate layers:

- scheduling
  Which compute resource or partition should run the job?
- sandboxing
  What parts of the filesystem should the job see?

## What a NORA queue is

A NORA queue is a queue name that appears in `main.conf` and that users see in NORA.

Examples from the config structure are:

- `DPXproc`
- `DPXimport`
- `acute`
- `patience`
- `gpujobs`

From the backend perspective, a queue name is just a logical label until NORA maps it to:

- an SGE queue
- or a Slurm partition

The backend code does this with:

- `SGE_QUEUES`
- `SLURM_QUEUES`

If a queue name is in `SLURM_QUEUES`, NORA treats it as a Slurm queue. If it is in `SGE_QUEUES`, NORA treats it as an SGE queue.

If it is in neither list, job submission fails.

## Minimal Slurm setup in `main.conf`

For a pure Slurm installation, the minimal queue-related settings in `main.conf` look like this:

```js
SGE_QUEUES:[],
SLURM_QUEUES:["DPXproc", "DPXimport"],

SLURM_INTERACTIVE_PARAMS:"--time 0-12 --cpus-per-task=4",

DEFAULTQUEUE:"DPXproc",
DEFAULTQUEUE_IMPORT:"DPXimport",

USEGRIDENGINE:1
```

### What these keys mean

#### `SLURM_QUEUES`

The list of queue names that NORA exposes and treats as Slurm-backed.

Example:

```js
SLURM_QUEUES:["DPXproc", "DPXimport"]
```

#### `SGE_QUEUES`

The list of queue names that NORA treats as SGE-backed.

For a pure Slurm setup, leave this empty:

```js
SGE_QUEUES:[]
```

#### `DEFAULTQUEUE`

The default queue for normal processing jobs.

#### `DEFAULTQUEUE_IMPORT`

The default queue for import-related jobs, especially DICOM import or autoexecution following import.

#### `SLURM_INTERACTIVE_PARAMS`

Default Slurm parameters for interactive jobs such as Jupyter or code-server.

Example:

```js
SLURM_INTERACTIVE_PARAMS:"--time 0-12 --cpus-per-task=4"
```

#### `USEGRIDENGINE`

Historical naming. Even in Slurm mode, this usually remains enabled because it controls whether NORA uses the scheduler layer at all.

## Mapping a NORA queue to a Slurm partition

Often you do not want user-facing queue names to be identical to the final Slurm partition names. NORA supports this with `SLURM_QUEUES_PARAMS`.

Example:

```js
SLURM_QUEUES:["acute","import","gpujobs"],

SLURM_QUEUES_PARAMS:{
  acute:{
    partition:"acute",
    params:"--mem 8GB --cpus-per-task 2"
  },
  import:{
    partition:"acute",
    params:"--mem 3GB --cpus-per-task 1"
  },
  gpujobs:{
    partition:"any",
    params:"--mem 16GB --cpus-per-task 4 --gres gpu:1"
  }
}
```

This means:

- users choose the NORA queue name such as `gpujobs`
- NORA maps it to the real Slurm partition such as `any`
- NORA appends the configured extra `sbatch` parameters

This is one of the most important concepts in the scheduling setup:

- a NORA queue is a user-facing abstraction
- a Slurm partition is the actual scheduler target

## Minimal `slurm.conf`

The Slurm side still needs a valid `slurm.conf` on the nodes where Slurm runs.

A minimal working example in the current style is:

```conf
ControlMachine=noradocker
AuthType=auth/munge
CryptoType=crypto/munge
ProctrackType=proctrack/linuxproc
ReturnToService=1
SlurmctldPidFile=/var/run/slurmctld.pid
SlurmctldPort=6817
SlurmdPidFile=/var/run/slurmd.pid
SlurmdPort=6818
SlurmdSpoolDir=/var/spool/slurmd
SlurmUser=slurm
StateSaveLocation=/var/lib/slurm
SwitchType=switch/none
TaskPlugin=task/none
MpiDefault=none
InactiveLimit=0
KillWait=30
MinJobAge=300
SlurmctldTimeout=120
SlurmdTimeout=300
Waittime=0
FastSchedule=1
SchedulerType=sched/backfill
SelectType=select/cons_res
SelectTypeParameters=CR_Core
AccountingStorageType=accounting_storage/none
AccountingStoreFlags=YES
ClusterName=cluster
JobCompType=jobcomp/none
JobAcctGatherFrequency=30
JobAcctGatherType=jobacct_gather/none
SlurmctldDebug=3
SlurmctldLogFile=/dpx/var/syslogs/slurmctld.log
SlurmdDebug=3
SlurmdLogFile=/dpx/var/syslogs/slurmd.log

NodeName=noradocker CPUs=4 State=UNKNOWN

PartitionName=DPXproc Nodes=noradocker Default=YES MaxTime=INFINITE State=UP
PartitionName=DPXimport Nodes=noradocker Default=YES MaxTime=INFINITE State=UP
```

You will need to adapt at least:

- `ControlMachine`
- `NodeName`
- CPU and resource definitions
- partition names
- log and spool paths

The partition names in Slurm should match either:

- the queue names directly
- or the `partition` values from `SLURM_QUEUES_PARAMS`

## A practical minimal Slurm rollout

If you want the smallest reasonable setup:

1. create a working Slurm partition for normal processing
2. create a second one for import jobs, or reuse the same partition
3. add those queue names to `SLURM_QUEUES`
4. set `DEFAULTQUEUE` and `DEFAULTQUEUE_IMPORT`
5. submit a trivial generic BASH job from NORA

The simplest example is:

```js
SLURM_QUEUES:["normal","import"],
DEFAULTQUEUE:"normal",
DEFAULTQUEUE_IMPORT:"import",
SLURM_QUEUES_PARAMS:{
  normal:{partition:"normal",params:"--cpus-per-task 1 --mem 4GB"},
  import:{partition:"normal",params:"--cpus-per-task 1 --mem 2GB"}
}
```

If you only want one partition at first:

```js
SLURM_QUEUES:["normal"],
DEFAULTQUEUE:"normal",
DEFAULTQUEUE_IMPORT:"normal"
```

That is often enough for first setup.

## How NORA chooses a queue

At runtime, NORA resolves the queue in roughly this order:

1. job-specific queue override
2. project-level queue
3. `DEFAULTQUEUE`
4. for imports, `DEFAULTQUEUE_IMPORT`

This means a queue can come from:

- the job definition
- the project configuration
- or the global config

That is why it is important to define sensible defaults even if power users may later override them.

## Interactive queues

Interactive jobs such as Jupyter or code-server often need different runtime settings than batch processing jobs. That is what `SLURM_INTERACTIVE_PARAMS` is for.

Typical example:

```js
SLURM_INTERACTIVE_PARAMS:"--time 0-12 --cpus-per-task=4"
```

This usually controls:

- wall time
- CPU count
- sometimes memory, if you include it

For many installations, it is wise to keep interactive jobs on a dedicated partition or a dedicated NORA queue so they do not compete with long-running compute jobs.

## Queue access restrictions

Some installations also define:

- `ADMIN_QUEUES`
- `RESTRICT_QUEUE_RIGHTS`

These are used to restrict which users may choose which queues. If you want a simple first setup, start without complicated queue-rights rules and only add them after the scheduler setup is stable.

## What the NORA jail is

The NORA jail is a per-job filesystem sandbox. Its goal is to avoid giving every job unrestricted access to the full host filesystem.

In the current implementation, the jail is created with Bubblewrap (`bwrap`) or a related chroot-like tool and is configured through `jail.conf`.

Conceptually, each job gets:

- a temporary jail root
- a curated set of read-write mounts
- a curated set of read-only mounts
- optional denied paths masked by tmpfs
- a temporary credentials file for database access

So the jail is not mainly about scheduling. It is about filesystem isolation.

## Minimal `jail.conf`

The current local style looks like:

```js
{
  jail: {
    runinjail:1,
    jailpath:"$DPXROOT/var/jails",
    mounts_rw : [ "/software" ],
    mounts_deny : [ "/software/slurm-20.02.5", "/software/notebooks" ],
    resources: {
      "HCPageDICOM": {
        source:"/nfs/data/dicomarchive/HCPaging",
        allowed:['hoven']
      }
    },
    mounts_ro : []
  }
}
```

The generic template is simpler:

```js
{
  jail: {
    runinjail:0,
    jailpath:"$DPXROOT/var/jails",
    max_shared_project_depth: 3,
    mounts_ro : [ "/software" ],
    mounts_rw : []
  }
}
```

For a first setup, start with something simple like:

```js
{
  jail: {
    runinjail:1,
    jailpath:"$DPXROOT/var/jails",
    mounts_ro:["/opt/software"],
    mounts_rw:["/shared/projects"],
    mounts_deny:[]
  }
}
```

Then only add complexity if a real use case requires it.

## Important jail settings

### `runinjail`

Enable or disable jailed job execution.

Example:

```js
runinjail:1
```

If set to `0`, jobs run without the Bubblewrap jail layer.

For debugging initial scheduler problems, it can be useful to temporarily disable the jail. Once the scheduler works, enable it again and fix the remaining mount issues.

### `jailpath`

Base directory where NORA creates per-job jail environments.

Example:

```js
jailpath:"$DPXROOT/var/jails"
```

This location must be writable by the backend.

### `mounts_ro`

Host paths mounted read-only into the jail.

Typical use:

- software installations
- atlases
- read-only templates

### `mounts_rw`

Host paths mounted read-write into the jail.

Typical use:

- shared project data
- scratch areas
- tool outputs

### `mounts_deny`

Paths that should be hidden or masked from the job even if they would otherwise be visible.

### `resources`

Optional explicit resource grants to selected users.

This is a more specialized mechanism for controlled access to particular host data trees.

### `max_shared_project_depth`

Controls how far shared-project access is traversed when collecting mounts for a job.

For most first setups, the template default is fine.

## What the jail actually mounts

At runtime, NORA combines several sources to build the jail mount list:

- project data folders
- shared project folders
- `mounts_rw`
- `mounts_ro`
- user-specific notebook folders for interactive jobs
- generated credentials and proc/dev bindings

This means the jail view is not only defined by `jail.conf`. It is the combination of:

- job context
- project access
- global jail config

## Required software for jails

The jail template comments explicitly note that jailed jobs need Linux user chroot support and Bubblewrap-style tooling.

The important practical point is:

- Bubblewrap or the configured jail tool must be installed on the worker nodes

The template comments also mention a common Slurm issue:

- some nodes do not create `/run/user/UID` in non-login scheduler contexts

In that case, parallelized jobs inside the jail may fail unless you enable lingering for the run user:

```bash
loginctl enable-linger <username>
```

This is especially relevant when `/dev/shm` and runtime directories are needed by tools inside the jail.

## A practical first jail rollout

For first setup, a good order is:

1. get Slurm submission working without jails
2. enable `runinjail:1`
3. start with only one read-only software mount and one read-write project mount
4. run a trivial generic BASH job
5. add more mounts only when the job shows a concrete missing path

This avoids building an overly permissive jail up front.

## Example minimal setup

### `main.conf`

```js
SLURM_QUEUES:["normal","import"],
DEFAULTQUEUE:"normal",
DEFAULTQUEUE_IMPORT:"import",
SLURM_INTERACTIVE_PARAMS:"--time 0-04 --cpus-per-task=2",
USEGRIDENGINE:1
```

### `slurm.conf`

```conf
NodeName=worker01 CPUs=8 State=UNKNOWN
PartitionName=normal Nodes=worker01 Default=YES MaxTime=INFINITE State=UP
PartitionName=import Nodes=worker01 Default=YES MaxTime=INFINITE State=UP
```

### `jail.conf`

```js
{
  jail: {
    runinjail:1,
    jailpath:"$DPXROOT/var/jails",
    mounts_ro:["/opt/software"],
    mounts_rw:["/shared/projects"],
    mounts_deny:[]
  }
}
```

This is enough to get a small Slurm-backed NORA installation running in many environments.

## Testing the setup

A practical test sequence is:

1. verify Slurm itself works with a manual `sbatch`
2. verify the NORA queue names match your intended Slurm partitions or queue mapping
3. submit a generic BASH job from NORA
4. confirm the log and error files appear under the NORA job log area
5. if jails are enabled, verify the job sees exactly the intended paths

For interactive services, also test:

- Jupyter launch
- code-server launch

because they are a quick way to inspect the jailed filesystem from inside a real job context.

## Common failure modes

- queue name exists in Slurm but not in `SLURM_QUEUES`
- queue name exists in NORA but maps to the wrong Slurm partition
- `DEFAULTQUEUE` or `DEFAULTQUEUE_IMPORT` is unset or wrong
- `sbatch` exists on the web node but not on the worker environment used by NORA
- `runinjail:1` is enabled but Bubblewrap is missing
- essential software or data paths were not added to `mounts_ro` or `mounts_rw`
- a denied path masks something that the job actually needs
- the jail path is not writable

## Relation to other documentation

Use [System Backend](system-backend.md) for service-level control of the instance.

Use [Jobs](jobs.md) and [Batchtool](batchtool.md) for user-facing job submission.

Use [Interactive Development Services](interactive-development-services.md) for Jupyter and code-server, which also depend on queues and jail mounts.

Use [Configuration Files](configuration-files.md) for the broader config file overview.
