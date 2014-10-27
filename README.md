# Dynamically update IP addresses


A small project to update my dynamic IP address. It currently only makes use of Rackspace CloudDNS


## Installation

Recommended to create a virtualenv and install the requirements (currently requests and pyrax)

```
# pip install requirements.txt
```

Now configure cron, systemd timers or anything else to run update.py at an interval

## Configuration

The configuration is stored in ~/.config/updateip.conf. Edit the following sample to get started

```
[config]
provider=rackspace

[rackspace]
username=rackspace_mycloud_username
apikey=rackspace_api_key

[domain_records]
example.com=www
cloud.net=test
```
