# Configuration Files

This chapter describes the local configuration files created and used by a NORA installation.

After `./install`, NORA creates its local configuration under `<path-to-nora>/conf`.

The current installer in `/nfs/norasys/unstable/bin/setup_localconf` creates these files automatically:

- `main.conf`: primary instance configuration, including module startup, MATLAB or Node.js backend selection, Docker ports, HTTPS, proxy settings, mounted paths, queue definitions, LDAP and sign-in behavior, and backup-related settings
- `pacs.conf`: DICOM receive and query configuration, including `storescp`, `pacsquery`, and project-routing filters for imported data
- `routes.conf`: host- and container-specific path mappings in `dir_routes` plus database host and port mappings in `db_routes`
- `smail.conf`: SMTP and notification mail settings
- `creds.conf`: database credentials and instance-local secrets such as `MASTERPASSWD`, shared PACS helper tokens, and session cookie migration settings
- `jail.conf`: optional Linux user-chroot isolation for processing jobs, including read-only and read-write mount lists
- `slurm.conf`: Slurm scheduler configuration used when Slurm runs inside Docker or when you want to keep a local Slurm config with the NORA checkout
- `gres.conf`: optional Slurm GRES definitions, for example GPU device mappings
- `version.conf`: internal software version tracking; this is maintained by NORA and normally should not be edited manually

Some practical guidance for the most important files:

- Start with `main.conf`, `routes.conf`, and `creds.conf`. These usually decide whether the instance boots successfully.
- Edit `pacs.conf` when you need DICOM receive nodes, PACS queries, or import filtering into target projects.
- Edit `smail.conf` if the platform should send emails or notifications that include absolute instance URLs.
- Edit `slurm.conf`, `gres.conf`, and `jail.conf` only if you use those features.


For the operational meaning of these files, use the dedicated chapters:

- [PACS and storescp Setup](pacs-storescp-setup.md) for `pacs.conf`
- [Slurm, Queues, and Jails](slurm-queues-and-jails.md) for `slurm.conf`, `gres.conf`, and `jail.conf`
- [Interactive Development Services](interactive-development-services.md) for `openssh.conf`, Jupyter, and code-server related setup
- [System Backend](system-backend.md) for the `dpxcontrol` commands that act on these configs

The current codebase also includes additional template-based configuration files that are feature-specific and may not be created automatically in every installation:

- `openssh.conf`: optional SSH `ForceCommand` injection used by `bin/runsshd.sh`
- `segmentationserver.conf`: remote segmentation service URL
- `llm_assist.conf`: request and rate-limit settings for the `llm_assist` feature

These template files live in `conf/templates/`. If you enable one of those features, create the corresponding local file in `conf/` and adapt it to your setup.


## Changing the database password

If you change the MySQL root password, update both MySQL user entries and the local credentials file:

1. On the host where the NORA Docker container is running, start a MySQL terminal:

   ```bash
   nora --admin mysql terminal
   ```

2. Run the password change statements in MySQL:

   ```sql
   ALTER USER 'root'@'localhost' IDENTIFIED BY 'NEW_PASSWORD';
   ALTER USER 'root'@'%' IDENTIFIED WITH mysql_native_password BY 'NEW_PASSWORD';
   FLUSH PRIVILEGES;
   ```

3. Update the password in `conf/creds.conf`, then restart the daemon so the NORA instance uses the new database credentials:

   ```bash
   nora --admin daemon restart
   ```
