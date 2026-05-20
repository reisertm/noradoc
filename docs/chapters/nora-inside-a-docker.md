# NORA inside a Docker

#### ​Install Docker on your host system

<span style="font-weight: 400;">First, install docker, git and jq on your host system</span>

`<span style="font-weight: 400;">sudo apt-get install docker.io git jq</span>`

<span style="font-weight: 400;">There might be an issue with the DNS address in docker. To check this, run</span>

`<span style="font-weight: 400;">docker run busybox nslookup google.com</span>`

<span style="font-weight: 400;">If the host cannot be reached, grep the address of your DNS server</span>

`<span style="font-weight: 400;">nmcli dev show | grep 'IP4.DNS'</span>`

<span style="font-weight: 400;">create the file </span><span style="font-weight: 400;">/etc/docker/daemon.json</span><span style="font-weight: 400;"> and insert the address as</span>

`<span style="font-weight: 400;">{</span>`

```<span style="font-weight: 400;">    "dns": ["yourDNSip", "8.8.8.8"]</span>`

`<span style="font-weight: 400;">}</span>`

<span style="font-weight: 400;">then restart docker</span>

`<span style="font-weight: 400;">sudo service docker restart</span>`

<span style="font-weight: 400;">go back to the busybox above and check if it works now.</span>

<span style="font-weight: 400;">Now, you should add your user to the docker group, otherwise you have not to </span>*<span style="font-weight: 400;">sudo</span>*<span style="font-weight: 400;"> all NORA commands </span>

`<span style="font-weight: 400;">sudo adduser <username> docker</span>`

<p class="callout warning">**!!! you have to re-login to make these changes apply !!!!!!**</p>



#### Clone the git repository

**NORA was historically named DPX. Note that this name might still often be used in the following.**<span style="font-weight: 400;"> Clone the repository into to a temp folder, or to your favorite program place.  
</span><span style="font-weight: 400;">Let's say we clone to your home directory into </span><span style="font-weight: 400;">~/nora</span>

`<span style="font-weight: 400;">git clone  https://<yourname>@bitbucket.org/reisert/dpx.git ~/nora</span>`

<span style="font-weight: 400;">If want to use NORA in a multi-user environment you might want to create a specific group (we usually use </span>*<span style="font-weight: 400;">dpxuser</span>*<span style="font-weight: 400;">) and change the group of that directory (recursivey) accordingly. </span><span style="font-weight: 400;">In any case, you have to set the s -flag and some ACLs recursively to that dir </span>*<span style="font-weight: 400;">(you might have to run this as sudo. In this case make sure to apply it to the correct ~/nora directory !! )</span>*

`<span style="font-weight: 400;">find ~/nora  -type d -exec  chmod g+s {} +</span>`

<span style="font-weight: 400;">If want to manage rights by ar group user</span>

`<span style="font-weight: 400;">chgrp -R NORA ~/nora # if you manage your right via usergroup NORA./dp</span>`

<span style="font-weight: 400;">nonetheless</span>

`<span style="font-weight: 400;">setfacl -R -d -m g::rwx ~/nora</span>`

#### Initial configuration

<span style="font-weight: 400;">Go into the nora directory and run </span><span style="font-weight: 400;">./install</span>

<span style="font-weight: 400;">This will create some local config files in the "conf" directory (for details see separate section below).</span>

<span style="font-weight: 400;"> NORA has 3 modules </span>

- **Frontend:** *<span style="font-weight: 400;">webserver with image viewer </span>*
- **DICOM node**<span style="font-weight: 400;"> to receive images from a PACS </span>
- **Backend:**<span style="font-weight: 400;"> processing module (depending on your preferences matlab or nodejs and slurm or SGE based)</span>

<span style="font-weight: 400;">By default, all three modules are enabled. To run NORA in this default configuration edit </span><span style="font-weight: 400;">main.conf</span><span style="font-weight: 400;"> and set at least </span><span style="font-weight: 400;">MATLABPATH: &lt;your-path-to-matlab&gt;</span>

<span style="font-weight: 400;">If you are behind a proxy, it might also be necessary to set the proxy (maybe even with user/password)</span>

`<span style="font-weight: 400;">DOCKER_http_proxy:" ... "</span>`

<span style="font-weight: 400;">Also set the user Nora should act as in the main.conf</span>

`<span style="font-weight: 400;">DPXUSER: " ... "</span><span style="font-weight: 400;"><br></br></span><span style="font-weight: 400;">DPXGROUP: " ... "</span>`

#### Build the docker image

<span style="font-weight: 400;">Your main function to control NORA is </span><span style="font-weight: 400;">dpxcontrol</span><span style="font-weight: 400;">. You can always run</span>

`<span style="font-weight: 400;">./dpxcontrol</span>`

<span style="font-weight: 400;">to get more help. To build the DOCKER image, first run</span>

`<span style="font-weight: 400;">./dpxcontrol docker build</span>`

<span style="font-weight: 400;">This will take a while. If everything went well, start all modules with</span>

`<span style="font-weight: 400;">./dpxcontrol start</span>`

<span style="font-weight: 400;">If something went wrong during installation / starts, there might be old 'zombie' containers. In this case you will be suggested docker commands to remove them. You can also start with </span><span style="font-weight: 400;">--force</span><span style="font-weight: 400;">to autoremove old NORA containers.</span>

<span style="font-weight: 400;">To check the status, now use</span>

`<span style="font-weight: 400;">./dpxcontrol status</span>`

<span style="font-weight: 400;">If at least the first point, Docker, is running nicely, you should be able to log into the Webinterface. (see below)</span>

#### Log into the Webinterface

<span style="font-weight: 400;">Now, open a web-browser and go to </span><span style="font-weight: 400;">localhost:81</span><span style="font-weight: 400;">. Default login is</span><span style="font-weight: 400;">  
  
</span><span style="font-weight: 400;">user</span>**:**<span style="font-weight: 400;"> root  
</span><span style="font-weight: 400;">password</span>**:**<span style="font-weight: 400;"> dpxuser</span>

<span style="font-weight: 400;">There are several options to create new users. You can either connect to an existing LDAP server, or just create users based on the internal user management of NORA (see Administration section for details). </span>

#### Troubleshooting and testing

<span style="font-weight: 400;">Most log files are written into</span>

`<span style="font-weight: 400;"><path-to-nora>/var/syslogs/</span>`

<span style="font-weight: 400;">These can also be seen from the </span>*<span style="font-weight: 400;">admin</span>*<span style="font-weight: 400;"> dialog at the top of the webinterface. </span>**If the daemon is not starting (or stopping again, red status) check the daemon.log for more info.**<span style="font-weight: 400;"> In case of a license error, maybe you have to forward your MAC adress to Docker (see </span><span style="font-weight: 400;">main.conf</span><span style="font-weight: 400;"> for more info)</span>

<span style="font-weight: 400;">For other system parts, there are also some test functions</span>

`<span style="font-weight: 400;">./dpxcontrol test [slurm | email | more_to_be_programmed]</span>`

#### Upgrade the database

<span style="font-weight: 400;">When your daemon is running nicely, it might be necessary to upgrade the initial database with</span>

`<span style="font-weight: 400;">./dpxcontrol matlab updatedb</span>`

#### Autostart on system startup

<span style="font-weight: 400;">To automatically start NORA when your computer starts, you can for example add </span><span style="font-weight: 400;">&lt;path-to-nora&gt;/dpxcontrol start --force</span> <span style="font-weight: 400;">to your </span><span style="font-weight: 400;">/etc/rc.local</span>

#### Slurm setup

<span style="font-weight: 400;">A proper configuration of slurm is a science on its own. Ask google for more information. If you are running slurm inside docker (default), the </span><span style="font-weight: 400;">conf/slurm.conf</span><span style="font-weight: 400;"> is used and you do not have to do too much. Otherwise, if docker is installed outside (this should be the correct practice) you have to it install via </span>

`<span style="font-weight: 400;">sudo apt-get install slurm-wlm</span>`

<span style="font-weight: 400;">on a deb-system and set </span>

`<span style="font-weight: 400;">DOCKER_run_daemon_in_docker: 0,</span>`

<span style="font-weight: 400;">in the </span><span style="font-weight: 400;">&lt;path-to-nora&gt;/conf/main.conf</span><span style="font-weight: 400;"> file. For configuring slurm itself there is a configurator interface via html, which you usually find here </span>

`<span style="font-weight: 400;">/usr/share/doc/slurmctld/slurm-wlm-configurator.easy.html</span>`

<span style="font-weight: 400;">which generates a conf file </span><span style="font-weight: 400;">/etc/slurm-llnl/slurm.conf</span><span style="font-weight: 400;"> where you have replace the hostname by the machine you are running NORA on. Further, the partitions have to specified. NORA has as default two partitions</span><span style="font-weight: 400;">  
</span><span style="font-weight: 400;">(computing queues) DPXproc and DPXimport, which have to specified in the slurm.conf like in this example:</span>

`<span style="font-weight: 400;"># COMPUTE NODES</span><span style="font-weight: 400;"><br></br></span><span style="font-weight: 400;">NodeName=hostname CPUs=8 State=UNKNOWN</span><span style="font-weight: 400;"><br></br></span><span style="font-weight: 400;">PartitionName=DPXproc Nodes=hostname Default=YES MaxTime=INFINITE State=UP</span><span style="font-weight: 400;"><br></br></span><span style="font-weight: 400;">PartitionName=DPXimport Nodes=hostname Default=YES MaxTime=INFINITE State=UP</span>`

<span style="font-weight: 400;">Alternatively, if you have an existing SLURM running with predefined paritions, you can change the paritions (queues) in NORA’s configuration in </span><span style="font-weight: 400;">&lt;path-to-nora&gt;/conf/main.conf (SLURM\_QUEUES)</span>

<span style="font-weight: 400;">Also consider </span>

`<span style="font-weight: 400;">./dpxcontrol test slurm </span>`

<span style="font-weight: 400;">for testing whether your slurm configuration is working.</span>

#### General Configuration

<span style="font-weight: 400;">All configuration files are located in </span><span style="font-weight: 400;">&lt;path-to-nora&gt;/conf</span><span style="font-weight: 400;"> directory. The configuration files are</span>

- <span style="font-weight: 400;">main.conf </span><span style="font-weight: 400;">- includes all major configurations, responsible for </span>
- <span style="font-weight: 400;">Location of external programs (MATLAB etc)</span>
- <span style="font-weight: 400;">DOCKER port forwarding</span>
- <span style="font-weight: 400;">Daemon beahviour</span>
- <span style="font-weight: 400;">Import behavior (dicoms etc)</span>
- <span style="font-weight: 400;">Mysql information</span>
- <span style="font-weight: 400;">signin/signup behaviour, LDAP configuration</span>
- <span style="font-weight: 400;">Backup behavior</span>

- <span style="font-weight: 400;">pacs.conf -</span><span style="font-weight: 400;"> includes all information how to connect to external dicom nodes</span>
- <span style="font-weight: 400;">routes.conf </span><span style="font-weight: 400;">- ip-addresses of DB, and routes of mount dirs (depending on hostnames diffferent mount locations are possible</span>
- <span style="font-weight: 400;">slurm.conf </span><span style="font-weight: 400;">- slurm configuration</span>
- <span style="font-weight: 400;">smail.conf </span><span style="font-weight: 400;">- mail configuration</span>
