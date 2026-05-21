# NORA inside a Docker

This chapter describes the Docker-based installation of NORA.

## Install Docker on the host system

Install Docker, Git, and `jq` on the host:

```bash
sudo apt-get install docker.io git jq
```

If Docker has DNS issues, test name resolution:

```bash
docker run busybox nslookup google.com
```

If the host cannot be reached, inspect your DNS server:

```bash
nmcli dev show | grep 'IP4.DNS'
```

Then create `/etc/docker/daemon.json` and add the DNS server:

```json
{
  "dns": ["yourDNSip", "8.8.8.8"]
}
```

Restart Docker:

```bash
sudo service docker restart
```

Then rerun the `busybox` test above.

Add your user to the Docker group so NORA commands do not require `sudo`:

```bash
sudo adduser <username> docker
```

> You must log out and back in again before this group change takes effect.

## Clone the repository

NORA was historically named `DPX`, and that name still appears in parts of the tooling and configuration.

For example, clone the repository into `~/nora`:

```bash
git clone https://<yourname>@bitbucket.org/reisert/dpx.git ~/nora
```

For multi-user installations, you may want to assign a shared group such as `dpxuser` and apply group-friendly permissions to the checkout:

```bash
find ~/nora -type d -exec chmod g+s {} +
chgrp -R NORA ~/nora
setfacl -R -d -m g::rwx ~/nora
```

Run these with `sudo` if needed, but make sure they target the correct `~/nora` directory.

## Initial configuration

Go into the NORA directory and run:

```bash
./install
```

This creates local configuration files in `conf/`.

NORA has three main modules:

- Frontend: web server with image viewer
- DICOM node: receives images from a PACS
- Backend: processing layer, depending on your MATLAB or Node.js setup and on Slurm or SGE

By default, all three modules are enabled. Edit `conf/main.conf` and set at least:

```text
MATLABPATH: <your-path-to-matlab>
```

If you are behind a proxy, you may also need:

```text
DOCKER_http_proxy: "..."
```

Also set the user and group NORA should run as:

```text
DPXUSER: "..."
DPXGROUP: "..."
```

Configuration files are documented separately in [Configuration Files](configuration-files.md).

## Build and start the Docker setup

The main control entrypoint is `dpxcontrol`. You can inspect available commands with:

```bash
./dpxcontrol
```

Build the Docker image:

```bash
./dpxcontrol docker build
```

Then start all modules:

```bash
./dpxcontrol start
```

If installation or startup failed previously, there may be stale containers left behind. In that case, use the suggested cleanup commands or start with `--force` to remove old NORA containers automatically.

Check the current status with:

```bash
./dpxcontrol status
```

If Docker starts correctly, the web interface should be reachable.

## Log in to the web interface

Open `http://localhost:81`.

Default credentials:

```text
user: root
password: dpxuser
```

You can later switch to LDAP or manage users with NORA's internal user management.

## Troubleshooting and testing

Most log files are written to:

```text
<path-to-nora>/var/syslogs/
```

They are also visible from the `admin` dialog in the web interface.

If the daemon starts and then stops again, check `daemon.log` first. If you see a license-related error, you may need to forward the host MAC address into Docker; see `main.conf`.

Some subsystems can also be tested explicitly:

```bash
./dpxcontrol test [slurm | email | more_to_be_programmed]
```

## Upgrade the database

Once the daemon is running correctly, you may need to upgrade the initial database:

```bash
./dpxcontrol matlab updatedb
```

## Start automatically on boot

One option is to add the following to `/etc/rc.local`:

```bash
<path-to-nora>/dpxcontrol start --force
```

## Slurm setup

Slurm can run inside Docker or on the host system.

If you use the default Docker-based setup, `conf/slurm.conf` is used and little extra configuration should be required.

If Slurm runs outside Docker, install it on Debian-based systems with:

```bash
sudo apt-get install slurm-wlm
```

Then set this in `conf/main.conf`:

```text
DOCKER_run_daemon_in_docker: 0
```

For Slurm configuration, you can use the configurator page usually located at:

```text
/usr/share/doc/slurmctld/slurm-wlm-configurator.easy.html
```

That typically generates a file at:

```text
/etc/slurm-llnl/slurm.conf
```

Replace the hostname with the machine running NORA and define the required partitions. By default, NORA expects two queues, `DPXproc` and `DPXimport`, for example:

```ini
# COMPUTE NODES
NodeName=hostname CPUs=8 State=UNKNOWN
PartitionName=DPXproc Nodes=hostname Default=YES MaxTime=INFINITE State=UP
PartitionName=DPXimport Nodes=hostname Default=YES MaxTime=INFINITE State=UP
```

If you already have an existing Slurm installation with predefined partitions, you can instead change NORA's configured queues in `conf/main.conf` via `SLURM_QUEUES`.

To test the Slurm configuration:

```bash
./dpxcontrol test slurm
```
