# dynamic-policy - Dynamic creation of SRX address entries

The SRX firewall can be configured to monitor a central web server for a list of IP Addresses to create a dynamic address book using the```security-intelligence```feature-set.

This software will need to be installed on an existing web-server and the python file modified to point to the correct base directory of the web-server. Clone all files and copy the schema.xml and manifest.xml file to the base of the web server. 

Configure the SRX security-intelligence module to point to you web server - the auth-token is required to commit (32 ascii chars), but is only used by Junos Space to authenticate the device:

```
set services security-intelligence url http://192.168.1.1/manifest.xml
set services security-intelligence authentication auth-token 12345678901234567890121234567890
```
The```manifest.xml```file provides a list of available "feeds" of IP addresses eg:

```
<manifest version="3540642feac48e76af183a6e79d55404">
  <category description="Customer category IPFilter" name="IPFilter" options="" ttl="2592000" update_interval="1">
    <config version="398490f188">
      <url>/schema.xml</url>
    </config>
    <feed data_ts="1428558808" name="BADSITES" objects="36" options="" types="ip_addr ip_range" version="BADSITES">
      <data>
        <url>/</url>
      </data>
    </feed>
  </category>
</manifest>
```

The SRX will refresh```manifest.xml``` every```update_interval```seconds, as specified in the manifest.

A feed is essentially a list of IPs that have some common purpose eg: a blacklist, whitelist, prefixes that identify a cloud provider etc.

Addresses are grouped into feeds and stored in independent feed files.

Within the SRX, a dynamic-address is created as follows:

```set security dynamic-address address-name MY-BLACKLIST profile category IPFilter feed BADSITES```

The SRX then consults the```manifest.xml```file for a feed named BADSITES, downloads it from the web server and then installs it into the dynamic-address entry.

The SRX will now consult the feed every update interval and dynamically add or remove addresses as they are available, all without requiring a configuration change.

**NOTE:** As of this writing this has been tested on Junos 12.3X48D10 and 15.1X49-D110 code releases, dynamic-address entries can only be used in security policies; NAT rules only consult the global and zone-based address-books for address entries.

# Usage
**Create a new feed**

```
dynamic-policy.py new MYFEED
```

**Add an address to a feed**

```
dynamic-policy.py add MYFEED 192.168.88.0/24
```

**Remove an address from a feed**

```
dynamic-policy.py del MYFEED 192.168.88.0/24
```
